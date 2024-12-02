# Automation Server Client

This is the automation server pip package that allows you to interface with the automation-server's API.

## Installation

You can install the package using pip:

```bash
pip install automation-server-client
```

## Usage
Here is a basic example of how to use the package:

```python
    # Set up configuration
    AutomationServerConfig.from_enviroment(
        fallback_url="http://localhost:8000/api", fallback_token=""
    )
    
    logging.basicConfig(level=logging.INFO, handlers = AutomationServerLoggingHandler(), logging.StreamHandler()])
    logger = logging.getLogger(__name__)

    ats = AutomationServer.from_environment()

    # Running locally, use a fixed workqueue_id
    if ats is None:
        ats = AutomationServer.debug(workqueue_id=1)
```

## Features

* Interface with the automation-server's API
* Retrieve process and workqueue status
* Retrieve work items for processing
* Logging actions and workitems

## Documentation
For detailed documentation, please visit Documentation Link.

## Contributing
Contributions are welcome! Please read the contributing guidelines first.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact
If you have any questions or feedback, please contact us at support@example.com.

