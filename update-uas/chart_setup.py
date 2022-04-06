#! /usr/bin/python
#
# MIT License
#
# (C) Copyright 2022 Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
""" Tool to build Helm Chart annotations based on default image list

MIT License

(C) Copyright [2021] Hewlett Packard Enterprise Development LP

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""
import sys
from getopt import getopt, GetoptError
import yaml


class UsageError(Exception):
    """Exception class to report usage errors.
    """


class OperationalError(Exception):
    """Exception class to report operational errors seen during execution.

    """


class MultiScalar(str):
    """Dummy class to re-type a string as a multiline scalar.  Used to
    present known multiline scalars to yaml for proper
    representation.

    """


def multiscalar_representer(dumper, data):
    """Special representer for multiline scalar strings.  This formats
    the string using pipe and multiple lines.
    """
    return dumper.represent_scalar(
        'tag:yaml.org,2002:str',
        data,
        style='|'
    )


# Register the multiline scalar representer with yaml
yaml.add_representer(MultiScalar, multiscalar_representer)


def read_values(chart_values):
    """Read in the chart values file (values.yaml) and return the result.

    """
    values = {}
    try:
        with open(chart_values, 'r', encoding='utf-8') as infile:
            values = yaml.load(infile, Loader=yaml.FullLoader)
    except OSError as err:
        raise OperationalError(
            "failed to load chart values '%s' - %s" %
            (chart_values, err)
        ) from err
    except yaml.YAMLLoadWarning as err:
        raise OperationalError(
            "failed to parse chart values '%s' - %s" %
            (chart_values, err)
        ) from err
    if not values or 'images' not in values:
        raise OperationalError(
            "chart values file '%s' does not contain valid data" %
            chart_values
        )
    return values


def render_chart_spec(chart_spec, values, version_tag):
    """Render as YAML the new chart specification using the information
    in 'values' and the image version tag in 'version_tag' and write
    it out to the new chart specification file (Chart.yaml).

    """
    chart = {}
    try:
        with open(chart_spec, 'r', encoding='utf-8') as infile:
            chart = yaml.load(infile, Loader=yaml.FullLoader)
    except OSError as err:
        raise OperationalError(
            "failed to load chart specification '%s' - %s" %
            (chart_spec, err)
        ) from err
    except yaml.YAMLLoadWarning as err:
        raise OperationalError(
            "failed to parse chart specification '%s' - %s" %
            (chart_spec, err)
        ) from err
    if not chart or 'apiVersion' not in chart:
        raise OperationalError(
            "chart specification file '%s' missing apiVersion" %
            chart_spec
        )
    if 'annotations' not in chart:
        raise OperationalError(
            "chart specification file '%s' missing annotations" %
            chart_spec
        )
    images = values.get('images', {})
    default_registry = "artifactory.algol60.net/csm-docker/stable"
    registry = images.get('registry', default_registry)
    image_list = images.get('list', [])
    composed_images = [
        dict(name=image, image="%s/%s:%s" % (registry, image, version_tag))
        for image in image_list
    ]
    if composed_images:
        rendered_images = MultiScalar(yaml.dump(composed_images))
        chart['annotations']['artifacthub.io/images'] = rendered_images
    try:
        with open(chart_spec, 'w', encoding='utf-8') as outfile:
            yaml.dump(chart, outfile)
    except OSError as err:
        raise OperationalError(
            "failed to update chart specification file '%s' - %s" %
            (chart_spec, err)
        ) from err


def render_chart_values(chart_values, values, version_tag):
    """Add the following content to 'values' and write the resulting data
    back to the chart_values file.

    """
    global_data = {
        'appVersion': version_tag
    }
    values['global'] = global_data
    try:
        with open(chart_values, 'w', encoding='utf-8') as outfile:
            yaml.dump(values, outfile)
    except OSError as err:
        raise OperationalError(
            "failed to update chart values file '%s' - %s" %
            (chart_values, err)
        ) from err

def usage(msg):
    """Present a usage message on stdout

    """
    if msg:
        sys.stdout.write("ERROR: %s\n" % msg)
    sys.stdout.write(
        "usage: chart_setup -t version-tag -c chart-spec -v chart-values\n"
        "\n"
        "Where:\n"
        "    -t version-tag\n"
        "       Specifies the application version tag\n"
        "\n"
        "    -c chart-spec\n"
        "       Specifies the path to the chart-specification\n"
        "       (Chart.yaml)\n"
        "       to be updated.\n"
        "\n"
        "    -v chart-values\n"
        "       Specifies the path to the chart-values (values.yaml)\n"
        "       to be used to obtain the list of UAI images\n"
    )


def main(argv):
    """Read in the Chart specificaiton file (typically Charts.yaml) and
    the Chart values file (typically values.yaml) and use the supplied
    'version' (typically the application build version of the repo) to
    fill out the

      annotations.artifacthub.io/images

    field in the Chart specification with a yaml string containing the
    list of UAI images from the Chart values with their versions
    set based on the same logic that is used in the jobs.yaml template
    file.

    Also update the chart values 'global.appVersion' field to specified
    version.
    """
    chart_spec = None
    version_tag = None
    chart_values = None
    try:
        opts, _ = getopt(argv, "c:t:v:")
    except GetoptError as err:
        raise UsageError(err) from err
    for opt in opts:
        if opt[0] == '-c':
            chart_spec = opt[1]
            continue
        if opt[0] == '-t':
            version_tag = opt[1]
            continue
        if opt[0] == '-v':
            chart_values = opt[1]
            continue
    if not chart_spec:
        raise UsageError("chart-specification path must be specified")
    if not version_tag:
        raise UsageError("version tag must be specified")
    if not chart_values:
        raise UsageError("chart-values path must be specified")
    values = read_values(chart_values)
    render_chart_spec(chart_spec, values, version_tag)
    render_chart_values(chart_values, values, version_tag)
    return 0

def entrypoint(argv):
    """Entrypoint used for error handling and exit status.

    """
    try:
        main(argv)
    except UsageError as err:
        usage(str(err))
        return 1
    except OperationalError as err:
        sys.stderr.write("ERROR: %s\n" % str(err))
        return 1
    return 0


# Start here
if __name__ == "__main__":   # pragma no unit test
    sys.exit(entrypoint(sys.argv[1:]))   # pragma no unit test
