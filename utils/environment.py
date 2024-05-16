import logging
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EnvironmentVariables:
    required_vars: List[str]
    env_vars: Dict[str, Optional[str]] = field(init=False)

    def __post_init__(self):
        self.env_vars = {}
        missing_vars = []

        for var in self.required_vars:
            value = os.environ.get(var)
            if value is None:
                missing_vars.append(var)
                logger.error("%s is not set or empty", var)
            self.env_vars[var] = value

        if missing_vars:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing_vars)}")

    def get(self, var_name: str) -> Optional[str]:
        """Retrieve the value of a specific environment variable."""
        return self.env_vars.get(var_name)
