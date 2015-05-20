import uuid

from boto.dynamodb2.exceptions import (
    ItemNotFound,
    ProvisionedThroughputExceededException,
)
from boto.dynamodb2.fields import (
    HashKey,
    RangeKey,
    GlobalKeysOnlyIndex,
)
from boto.dynamodb2.table import Table
from boto.exception import JSONResponseError
from devmgr.models.device import Device
from devmgr.models.token import SessionToken
from tornado import gen


def create_session_table(name='sessions', table_read_throughput=5,
                         table_write_throughput=5, token_read_throughput=5,
                         token_write_throughput=5):
    return Table.create(
        name,
        schema=[HashKey('device_id', data_type='B')],
        throughput=dict(
            read=table_read_throughput,
            write=table_write_throughput,
        ),
        global_indexes=[GlobalKeysOnlyIndex(
            'SessionTokenIndex',
            parts=[HashKey('device_id', data_type='B')],
            throughput=dict(
                read=token_read_throughput,
                write=token_write_throughput,
            )
        )]
    )


def create_device_table(name='devices', read_throughput=5, write_throughput=5):
    return Table.create(
        name,
        schema=[HashKey('user_id'), RangeKey('device_id')],
        throughput=dict(
            read=read_throughput,
            write=write_throughput,
        )
    )


class SessionStore:
    def __init__(self, executor, table, key_manager):
        self.executor = executor
        self.table = table
        self.key_manager = key_manager

    @gen.coroutine
    def get(self, token_id):
        record = None
        try:
            record = yield self.executor.submit(
                self._get_session,
                token_id,
            )
        except ProvisionedThroughputExceededException:
            # TODO: Add metrics.
            raise

        token = SessionToken.from_bytes(self.key_manager, record['data'])
        token.update(
            device_id=uuid.UUID(bytes=record['device_id']),
            created_at=int(record['created_at'])
        )
        return token

    @gen.coroutine
    def put(self, token):
        result = False
        try:
            result = yield self.executor.submit(
                self.table.connection.put_item,
                self.table.table_name,
                item=dict(
                    data={'B': token.to_bytes()},
                    device_id={'B': token.device_id.bytes},
                    created_at={'N': str(token.created_at)}
                )
            )
        except ProvisionedThroughputExceededException:
            # TODO: Add metrics.
            raise
        return result

    @gen.coroutine
    def delete(self, token):
        try:
            yield self.executor.submit(
                self.table.delete_item,
                device_id=token.device_id,
                expected=dict(token_id__eq=token.token_id)
            )
            return True
        except ProvisionedThroughputExceededException:
            return False

    def _get_session(self, token_id):
        records = self.table.query_2(
            token_id__eq=token_id,
            index='SessionTokenIndex',
            limit=1
        )
        return next(records, None)


class DeviceStore:
    def __init__(self, executor, table):
        self.executor = executor
        self.table = table

    @gen.coroutine
    def get_all(self, user_id):
        records = None
        try:
            records = yield self.executor.submit(self._get_devices, user_id)
        except ProvisionedThroughputExceededException:
            # TODO: Add metrics.
            raise
        return records

    @gen.coroutine
    def get(self, user_id, device_id):
        record = None
        try:
            record = yield self.executor.submit(
                self.table.get_item,
                consistent=True,
                user_id=user_id,
                device_id=device_id,
            )
        except (ItemNotFound, JSONResponseError):
            pass
        except ProvisionedThroughputExceededException:
            # TODO: Add metrics.
            raise
        return self._to_device(record) if record else None

    @gen.coroutine
    def put(self, device):
        try:
            self.table.connection.put_item(
                self.table.table_name,
                item=dict(
                    user_id={'S': device.user_id},
                    device_id={'B': device.device_id.bytes},
                    name={'S': device.name},
                    kind={'S': device.kind},
                    session_id={'S': device.session_id},
                    push_endpoint={'S': device.push_endpoint},
                )
            )
        except ProvisionedThroughputExceededException:
            # TODO: Add metrics.
            raise

    @gen.coroutine
    def delete(self, device):
        try:
            yield self.executor.submit(
                self.table.delete_item,
                user_id=device.user_id,
                device_id=device.device_id.bytes,
            )
            return True
        except ProvisionedThroughputExceededException:
            return False

    def _get_devices(self, user_id):
        query = self.table.query_2(
            consistent=True,
            user_id__eq=user_id,
            device_id__gt=' ',
        )
        return map(self._to_device, query)

    def _to_device(self, record):
        return Device(
            user_id=record['user_id'],
            device_id=uuid.UUID(bytes=record['device_id']),
            name=record['name'],
            kind=record['kind'],
            session_id=record['session_id'],
            push_endpoint=record['push_endpoint'],
        )
