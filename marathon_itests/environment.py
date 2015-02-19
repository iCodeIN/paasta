import time


def before_all(context):
    # TODO: Maybe be smarter and unblock when the marathon port is open?
    print "Sleeping 10 seconds to allow marathon to start up."
    time.sleep(10)


def after_scenario(context, scenario):
    """If a marathon client object exists in our context, delete any apps in Marathon and wait until they die."""
    if context.client:
        while True:
            apps = context.client.list_apps()
            if not apps:
                break
            for app in apps:
                context.client.delete_app(app.id, force=True)
            time.sleep(0.5)
        while context.client.list_deployments():
            time.sleep(0.5)
