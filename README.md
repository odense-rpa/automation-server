# Automation Server

[![Version](https://img.shields.io/badge/version-0.4.1-blue.svg)](https://github.com/odense-rpa/automation-server)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-beta-orange.svg)](https://github.com/odense-rpa/automation-server/issues)
[![Documentation](https://img.shields.io/badge/docs-live-blue.svg)](https://odense-rpa.github.io/automation-server/)

<a href="website/static/img/main-interface.png"><img src="website/static/img/main-interface.png" width="400px" style="float: right; margin: 0.5em;"></a>

Automation Server allows you to build, run and monitor automations written in python. Easily orchestrate your automations and deploy them on workers dynamically. Jobs get routed to workers based on their capabilities and resources are automatically utilized.


- **Web Interface:** At a single glance you can monitor status, trigger automations and see the overall health of your cluster. Manage all aspects of your automations
- **Automations on time:** Use powerful cron based triggers to ensure your automations run when you want them to. You can also trigger on specific date and times. Workqueues provide flexible triggering based on the amount of work to do.
- **Audit your automations:** Built-in logging and integration with Pythons logging system provides a clear audit-trail. All logs are grouped by their sessions and associated workitems allowing for ease if access and operations.
- **Templates for automations:** Automation Server provides a framework for interacting with the server from your processes. There is also a [template](https://github.com/odense-rpa/process-template) to get you started.
- **Isolated execution:** Each worker runs a single automation at the time and it is isolated in it's private environment, thus ensuring stability and package integrity.
- **Secure credential storage:** Store credentials for your automations centrally, encrypted at rest with an optional server-side encryption key.

## Get started

Full documentation is at **https://odense-rpa.github.io/automation-server/** — see the [installation guide](https://odense-rpa.github.io/automation-server/docs/getting-started/installation) to get up and running.

## Next steps

Once installed, check out the [process template](https://github.com/odense-rpa/process-template) to build your first automation, or add the [test process](https://github.com/odense-rpa/test-process) to explore scheduling features.


If you require assistance feel free to create a [discussion](https://github.com/odense-rpa/automation-server/discussions) or open an [issue](https://github.com/odense-rpa/automation-server/issues).


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Check our [issues](https://github.com/odense-rpa/automation-server/issues) for planned features
2. Open an issue to discuss your idea
3. Fork the repository and create a feature branch
4. Make your changes and add tests
5. Submit a pull request

For detailed documentation, visit the [documentation site](https://odense-rpa.github.io/automation-server/).