# (Maybe Good) Agent Utils

This repository contains a collection of utilities, scripts, and resources for working with agents within IDEs.

## 🧰 Utilities

Each utility comes with its own usage instructions. Please refer to the documentation:

- **📈 Rules Analytics**: ([Docs](docs/util-rules-analytics.md), [Source](.agent/utils/rules_analytics.py))
  - Helps you understand:
    - Which rules are being used e.g. `my-rule.mdc`
    - By which agents e.g. `cursor`, `roo-code`
    - How frequently e.g. `10 times`
  - How it works:
    - There is a prompt that's added to your agent's configuration or included in an "always apply" rule
    - The simple prompt instructs the agent to run a terminal command e.g.:
      - `python rules_analytics.py write --filename "my-rule.mdc" --by "cursor"`
    - When the command is run, it writes the rule usage data to a JSON file called `rules_analytics.json`
    - Use this data to optimize your rules and improve agent performance

## 🤝 Contributing

Contributions are welcome! Please feel free to submit an Issue or Pull Request.

## 📄 License

This project is licensed under the [MIT License](LICENSE).