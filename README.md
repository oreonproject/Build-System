# Oreon Build System

## Features

- **Modern Web UI**: Sleek, responsive interface with glass morphism design
- **RPM Package Building**: Full support for building RPM packages from various sources
- **ISO Builder**: Integrated ISO creation using livemedia-creator and kickstart files
- **Mass Packaging**: Build and manage multiple packages as unified projects
- **Automated Workflows**: Streamlined build processes with comprehensive logging
- **Repository Management**: Automatic repository creation and dependency resolution

## Quick Start

### Using Docker (Recommended)

```bash
git clone https://github.com/oreonproject/oreon-build-system.git
cd oreon-build-system
docker-compose up -d
```

### Manual Installation

1. Install dependencies
2. Configure the database
3. Start the services

## Building Packages

### Single Package Build
1. Create a new project
2. Upload your .spec file or provide source URL
3. Select target architectures and distributions
4. Submit build

### Mass Package Build
1. Create a project group
2. Add multiple packages to the group
3. Configure dependencies and build order
4. Submit batch build

### ISO Creation
1. Upload your kickstart (.ks) file
2. Configure ISO parameters
3. Select base repositories
4. Build your custom ISO

## Architecture

The Oreon Build System consists of:

- **Frontend**: Modern Flask web application with responsive UI
- **Backend**: Python-based build orchestration system
- **Builder Nodes**: Mock-based build environment
- **Storage**: Package and ISO repository management

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

Licensed under the GPL v2+ - see the [LICENSE](LICENSE) file for details.

## Community

- **Forum**: [forums.oreonproject.org](https://forums.oreonproject.org)
