# sbo-tests

## Description of sbo-dom-checks.json

The DOM elements to check are described in this file as a list.

```
[
    [
        "/path/to/page",
        [
            ["find-method", "element-selector", "operator", count]
        ]
    ]
]
```

* /path/to/page should be self-explanatory.
* find-method can be any method supported by selenium's `driver.find_element` - see [the selenium documentation](https://selenium-python.readthedocs.io/locating-elements.html).
* element-selector depends on the find-method used. See, once again, [the selenium documentation](https://selenium-python.readthedocs.io/locating-elements.html).
* operator (optional): one of >=, <=, <, >, = to determine how to interpret count
* count: an integer specifying whether the number of elements found should be <operator>count

Acknowledgements
================

The development of this software was supported by funding to the Blue Brain Project, a research center of the École polytechnique fédérale de Lausanne (EPFL), from the Swiss government’s ETH Board of the Swiss Federal Institutes of Technology.

For license see LICENSE.txt.

Copyright (c) 2013-2024 Blue Brain Project/EPFL
