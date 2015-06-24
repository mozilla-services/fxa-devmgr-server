import json

from devmgr.resources import Registration, Device


def new_device(context, request):
    data = json.loads(request.body)
    device = context.new_device(request.credentials.account_id, data["name"],
                                data.get("endpoint"))
    return {"device-id": device.uuid}


def list_devices(context, request):
    return dict(devices=[x.to_json() for x in context.all_devices()])


def delete_device(context, request):
    request.db.delete(context)
    return {}


def update_device_metadata(context, request):
    data = json.loads(request.body)
    context.endpoint = data["endpoint"]
    return {}


def include_views(config):
    config.add_view(new_device, context=Registration, permission="create",
                    request_method="POST")
    config.add_view(list_devices, context=Registration, permission="get",
                    request_method="GET")
    config.add_view(delete_device, context=Device, permission="delete",
                    request_method="DELETE")
    config.add_view(update_device_metadata, context=Device,
                    permission="update", request_method="PATCH")
