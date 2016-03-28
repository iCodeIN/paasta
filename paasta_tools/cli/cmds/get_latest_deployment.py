#!/usr/bin/env python
# Copyright 2015 Yelp Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from paasta_tools.cli.utils import lazy_choices_completer
from paasta_tools.cli.utils import list_services
from paasta_tools.cli.utils import PaastaColors
from paasta_tools.cli.utils import validate_service_name
from paasta_tools.generate_deployments_for_service import get_latest_deployment_tag
from paasta_tools.remote_git import list_remote_refs
from paasta_tools.utils import DEFAULT_SOA_DIR
from paasta_tools.utils import get_git_url


def add_subparser(subparsers):
    list_parser = subparsers.add_parser(
        'get-latest-deployment',
        help='Gets the Git SHA for the latest deployment of a service',
    )
    list_parser.add_argument(
        '-s', '--service',
        help='Name of the service which you want to get the latest deployment for.',
        required=True,
    ).completer = lazy_choices_completer(list_services)
    list_parser.add_argument(
        '-i', '--deploy-group',
        help='Name of the deploy group which you want to get the latest deployment for.',
        required=True,
    )
    list_parser.add_argument(
        '-d', '--soa-dir',
        help='A directory from which soa-configs should be read from',
        default=DEFAULT_SOA_DIR,
    )

    list_parser.set_defaults(command=paasta_get_latest_deployment)


def paasta_get_latest_deployment(args):
    service = args.service
    deploy_group = args.deploy_group
    soa_dir = args.soa_dir
    validate_service_name(service, soa_dir)

    git_url = get_git_url(
        service=service,
        soa_dir=soa_dir,
    )
    remote_refs = list_remote_refs(git_url)

    _, git_sha = get_latest_deployment_tag(remote_refs, deploy_group)
    if not git_sha:
        print PaastaColors.red("A deployment could not be found for %s in %s" % (deploy_group, service))
        return 1
    else:
        print git_sha
        return 0
