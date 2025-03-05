import logging
from datetime import datetime
from functools import partial, reduce
from operator import getitem
from pathlib import Path

from logger import setup_logging
from utils import read_json, write_json


class ConfigParser:

    def __init__(self, config, modification=None, run_id=None):

        self._config = _update_config(config, modification)

        save_dir = Path(self.config["save_dir"])
        exper_name = self.config["name"]
        if run_id is None:
            run_id = datetime.now().strftime(r"%m%d_%H%M%S")

        self._log_dir = save_dir / "log" / exper_name / run_id

        exist_ok = run_id == ""
        self.log_dir.mkdir(parents=True, exist_ok=exist_ok)

        write_json(self.config, save_dir / "config.json")

        setup_logging(self.log_dir)
        self.log_levels = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}

    def get_logger(self, name, verbosity=2):
        msg_verbosity = "verbosity option {} is invalid. Valid options are {}.".format(
            verbosity, self.log_levels.keys()
        )
        # log level 에 verbosity 가 없으면 메시지 출력
        assert verbosity in self.log_levels, msg_verbosity
        logger = logging.getLogger(name)
        logger.setLevel(self.log_levels[verbosity])
        return logger

    @classmethod
    def from_args(cls, args, options=""):
        for opt in options:
            args.add_argument(*opt.flags, default=None, type=opt.type)
        if not isinstance(args, tuple):
            args = args.parse_args()
        # config.json 없으면 메시지 출력
        msg_no_config = "Configuration file is required. Add '-c config.json'"
        assert args.config is not None, msg_no_config
        config_fname = Path(args.config)

        config = read_json(config_fname)
        if args.config:
            config.update(read_json(args.config))
        if args.port:
            config["port"] = args.port
        if args.host:
            config["host"] = args.host

        modification = {
            opt.target: getattr(args, _get_opt_name(opt.flags)) for opt in options
        }
        return cls(config, modification)

    def __getitem__(self, name):
        return self.config[name]

    def init_obj(self, name, module, *args, **kwargs):
        module_name = self[name]["type"]
        module_args = dict(self[name]["args"])
        assert all(
            [k not in module_args for k in kwargs]
        ), "Overwriting kwargs given in config file is not allowed"
        module_args.update(kwargs)
        return getattr(module, module_name)(*args, **module_args)

    @property
    def config(self):
        return self._config

    @property
    def port(self):
        return self._port

    @property
    def host(self):
        return self._host

    @property
    def log_dir(self):
        return self._log_dir


def _update_config(config, modification):
    if modification is None:
        return config

    for key, value in modification.items():
        if value is not None:
            _set_by_path(config, key, value)
    return config


def _set_by_path(tree, keys, value):
    keys = keys.split(";")
    _get_by_path(tree, keys[:-1])[keys[-1]] = value


def _get_by_path(tree, keys):
    return reduce(getitem, keys, tree)


def _get_opt_name(flags):
    for flg in flags:
        if flg.startswith("--"):
            return flg.replace("--", "")
    return flags[0].replace("--", "")
