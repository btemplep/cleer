"""cleer - A customizable and extensible file formatter.

```python
from cleer import Cleer, cleer_default_config


clr = Cleer(config=cleer_default_config(python_packages=["my_package"]))
results = clr.format("src/")
```
"""

__version__ = "0.1.0a9"

__all__ = [
    "Cleer",
    "cleer_default_config"
]

from loguru import logger


logger.disable("cleer")

from cleer.cleer import Cleer
from cleer.default import cleer_default_config
from cleer.exceptions import *
from cleer.exceptions import __all__ as exceptions_all
from cleer.formatters import *
from cleer.formatters import __all__ as formatters_all
from cleer.tokenizers import *
from cleer.tokenizers import __all__ as tokenizers_all
from cleer.types import *
from cleer.types import __all__ as types_all
from cleer.validators import *
from cleer.validators import __all__ as validators_all


__all__ += formatters_all
__all__ += exceptions_all
__all__ += tokenizers_all
__all__ += types_all
__all__ += validators_all
