
import sys
import yaml
import semver

repo_map = {
    '999999999999.dkr.ecr.eu-west-2.amazonaws.com/foobar': ['8.2.0', '8.1.2', '8.1.1']
}


def get_latest_semver(l):
    v = sorted(map(semver.VersionInfo.parse, l))
    return v[-1]


def policy_all(current, args):
    if current is None:
        raise ValueError("Policy 'all' requires semver, but {} is not semver".format(
            self.literal_version))
    available = repo_map[args['registry']]
    latest = get_latest_semver(available)
    if latest > current:
        return latest
    return current


policies = {
    'all':  policy_all,
}


class SeelTag(yaml.YAMLObject):
    yaml_tag = u'!seel'

    def __init__(self, source):
        parts = source.split(' ')
        self.literal_version = parts.pop(-1)
        try:
            self.version = semver.VersionInfo.parse(self.literal_version)
        except ValueError:
            self.version = None  # not semver
        self.args = {}
        for i in parts:
            argparts = i.split('=', 1)
            if(len(argparts) != 2):
                raise SyntaxError("Seel: Unable to parse arg {0}".format(i))
            self.args[argparts[0]] = argparts[1]
        self.policy = self.args.get('policy', 'all')

    def as_yaml(self):
        policy = policies[self.policy]
        new_version = policy(self.version, self.args)
        return "{} {}".format(" ".join(map("=".join, self.args.items())),
                              new_version
                              )

    def __repr__(self):
        return "'%s'" % self.source

    @classmethod
    def from_yaml(cls, loader, node):
        return SeelTag(node.value)

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_scalar(cls.yaml_tag, data.as_yaml())


yaml.SafeLoader.add_constructor('!seel', SeelTag.from_yaml)
yaml.SafeDumper.add_multi_representer(SeelTag, SeelTag.to_yaml)

y = yaml.safe_load(open("sample.yaml"))

s = yaml.safe_dump(y, default_flow_style=False, width=160)

print(s)
