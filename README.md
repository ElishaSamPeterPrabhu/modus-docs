# Modus Document Code

A comprehensive documentation repository for Modus Web Components, containing extracted documentation, component specifications, and automated documentation generation tools.

## 🎯 Purpose

This repository serves as a centralized hub for:
- **Complete Modus Web Components Documentation** - All framework guides, component docs, and examples
- **Component Specifications** - Detailed JSON specifications for all 44+ Modus components
- **Documentation Generation Tools** - Automated scripts to keep documentation up-to-date
- **Framework Integration Examples** - Working examples for React, Angular, and Vue

## 📁 Repository Structure

```
modus-document-code/
├── docs/                          # Complete extracted documentation
│   ├── components/                # Individual component README files (44 components)
│   ├── frameworks/                # Framework-specific integration guides
│   │   ├── react/                # React v17, v18, v19 documentation
│   │   ├── angular/              # Angular ng17, ng18, ng19 documentation
│   │   └── vue/                  # Vue integration documentation
│   ├── getting-started/          # Getting started guides and tutorials
│   ├── icons/                    # Icons catalog and usage documentation
│   ├── examples/                 # Working code examples
│   │   ├── react/               # React component examples
│   │   └── vue/                 # Vue component examples
│   ├── general/                  # General project documentation
│   └── _documentation_index.json # Complete catalog of all documentation
├── data/                         # Component specifications and data
│   └── component-docs/          # JSON specifications for all components
├── scripts/                      # Documentation generation and maintenance tools
│   ├── src/                     # Core parsing and analysis modules
│   ├── update_modus_components.py # Component documentation updater
│   └── extract_all_docs.py     # Complete documentation extractor
├── examples/                     # Additional examples and templates
└── requirements.txt             # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Git
- Internet connection (for fetching latest Modus source)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/modus-document-code.git
   cd modus-document-code
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Update documentation (optional):**

   ```bash
   python scripts/update_modus_components.py
   python scripts/extract_all_docs.py
   ```

## Running the Documentation Server

To run the local documentation server:

1. **Create a virtual environment:**

   ```bash
   python3 -m venv venv
   ```

2. **Activate the virtual environment:**

   ```bash
   # On macOS/Linux
   source venv/bin/activate
   
   # On Windows
   venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Start the server:**

   ```bash
   python3 modus_docs_server.py
   ```

The server will start on `http://localhost:8000` by default.

## 📚 Documentation Overview

### Component Documentation (44 Components)

Complete documentation for all Modus Web Components:

- **Form Components**: Button, Text Input, Number Input, Select, Checkbox, Radio, Switch, Textarea, Date Input, Time Input, Autocomplete
- **Navigation**: Navbar, Side Navigation, Breadcrumbs, Tabs, Menu, Menu Item, Pagination
- **Display**: Card, Table, Typography, Avatar, Badge, Chip, Divider, Icon, Loader, Progress, Rating, Skeleton
- **Feedback**: Alert, Toast, Tooltip, Modal, Input Feedback, Input Label
- **Layout**: Accordion, Collapse, Stepper, Toolbar, Utility Panel
- **Interactive**: Dropdown Menu, Slider, Theme Switcher

### Framework Integration Guides

#### React Integration
- **React 17, 18, 19** - Complete setup and usage guides
- **Component Examples** - Working React component examples
- **Best Practices** - React-specific implementation patterns

#### Angular Integration  
- **Angular 17, 18, 19** - Version-specific integration guides
- **Value Accessor Bindings** - Form integration patterns
- **Module Setup** - Complete Angular module configuration

#### Vue Integration
- **Vue 3** - Latest Vue integration guide
- **Component Examples** - 42 complete Vue component examples
- **Plugin Configuration** - Vue plugin setup and usage

### Icons Documentation

- **25 Icons** cataloged across 4 categories:
  - **Solid Icons** (18): Navigation, alerts, actions
  - **Outline Icons** (3): Info, warning, check states  
  - **Theme Icons** (2): AI dark/light variants
  - **Branding Icons** (2): Trimble logos
- **Usage Guide** - Complete icon implementation guide

## 🛠️ Documentation Generation Tools

### Component Documentation Updater

```bash
python scripts/update_modus_components.py
```

**Features:**
- Automatically fetches latest Modus Web Components source from GitHub
- Extracts component properties, events, methods, and slots
- Updates JSON specifications for all components
- Handles git conflicts and repository management

### Complete Documentation Extractor

```bash
python scripts/extract_all_docs.py
```

**Features:**
- Extracts all documentation from Modus repository
- Organizes content by framework, component, and purpose
- Creates searchable documentation index
- Preserves examples and code samples

## 📊 Documentation Statistics

- **123 Total Files** extracted and organized
- **44 Components** fully documented
- **25 Icons** cataloged and categorized
- **3 Frameworks** (React, Angular, Vue) with complete integration guides
- **46 Code Examples** across frameworks
- **11 General Documentation** files (contributing, security, etc.)

## 🔄 Keeping Documentation Updated

The documentation in this repository can be kept up-to-date with the latest Modus Web Components:

1. **Automatic Updates**: Run the update scripts periodically
2. **CI/CD Integration**: Set up automated updates using GitHub Actions
3. **Manual Updates**: Use the provided scripts when needed

### Update Workflow

```bash
# Update component specifications
python scripts/update_modus_components.py

# Extract all documentation  
python scripts/extract_all_docs.py

# Commit changes
git add .
git commit -m "Update documentation from latest Modus source"
git push
```

## 📖 Usage Examples

### Finding Component Documentation

```bash
# View all available components
cat data/component-docs/_all_components.json

# Read specific component documentation
cat docs/components/modus-wc-button-README.md
```

### Framework-Specific Guides

```bash
# React integration
cat docs/frameworks/react/react.mdx

# Angular integration  
cat docs/frameworks/angular/angular.mdx

# Vue integration
cat docs/frameworks/vue/vue.mdx
```

### Working Examples

```bash
# React examples
ls docs/examples/react/

# Vue examples  
ls docs/examples/vue/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Update documentation if needed
5. Submit a pull request

## 📄 License

This project follows the same license as Modus Web Components - MIT License.

## 🔗 Related Resources

- [Modus Web Components](https://github.com/trimble-oss/modus-wc-2.0)
- [Modus Design System](https://modus.trimble.com/)
- [Component Documentation](https://trimble-oss.github.io/modus-wc-2.0/main)

## 🐳 Docker Support

### Building the Docker Image

```bash
docker build -t modus-docs-server .
```

### Running the Container

```bash
# Run with default settings (port 8000)
docker run -p 8000:8000 modus-docs-server

# Run with custom port
docker run -p 3000:3000 -e PORT=3000 modus-docs-server

# Run in detached mode
docker run -d -p 8000:8000 --name modus-docs modus-docs-server
```

### Environment Variables

- `HOST` - Server host address (default: `0.0.0.0`)
- `PORT` - Server port (default: `8000`)

### Docker Compose Example

```yaml
version: '3.8'
services:
  modus-docs:
    build: .
    ports:
      - "8000:8000"
    environment:
      - HOST=0.0.0.0
      - PORT=8000
    restart: unless-stopped
```

## 📞 Support

For questions about this documentation repository:
- Create an issue in this repository
- Refer to the original Modus Web Components documentation
- Check the framework-specific integration guides

---

**Last Updated**: Auto-generated from Modus Web Components main branch
**Total Components**: 44
**Total Documentation Files**: 123

