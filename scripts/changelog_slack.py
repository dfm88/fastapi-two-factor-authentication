import json
import re
import sys


# Function to format a markdown link to a Slack link
def markdown_to_slack_link(text):
    """
    Replace markdown links with Slack links. For example, [text](url) becomes <url|text>.
    It skips links that contain the word "skip".
    """
    return re.sub(r"\[((?!skip).+?)\]\((.+?)\)", r"<\2|\1>", text)


def markdown_to_slack_header(text):
    return re.sub(r"# (.+?)\n\n", r"\1", text).lstrip("# ").strip()


def format_changelog_for_slack(changelog_content: str) -> dict:
    # Prepare the Slack message blocks (to test output go to https://app.slack.com/block-kit-builder)
    slack_blocks = [{"type": "header", "text": {"type": "plain_text", "text": "📝 Changelog"}}]
    # remove html comments
    changelog_content = re.sub(r"<!--.*?-->", "", changelog_content, flags=re.DOTALL)
    # remove   - (=) on the end of the lines
    changelog_content = re.sub(r" - \(=\)", "", changelog_content)
    # Replace all words surrounded by two ** with the same words surrounded by *
    changelog_content = re.sub(r"\*\*(.*?)\*\*", r"*\1*", changelog_content)
    # Find version headers
    versions = re.findall(r"(# .+?\n\n)(.+?)(?=\n# |$)", changelog_content, re.DOTALL)
    # find this pattern # [1.3.0](https://github.com/altacucina/backend/compare/1.2...1.3.0) - (2024-03-07)
    tag = re.findall(r"# \[(.+?)\]\((.+?)\)", changelog_content, re.DOTALL)
    for version_header, content in versions:
        # Add version header to Slack blocks
        version_text = markdown_to_slack_header(version_header.strip())
        if "changelog" not in version_text.lower():
            slack_blocks.append({"type": "header", "text": {"type": "plain_text", "text": version_text}})
        slack_blocks.append({"type": "divider"})
        slack_blocks.append({"type": "divider"})

        # extract the line with the new tag
        tag_pattern = r"# \[(\d+\.\d+\.\d+)\].*"
        tag = re.search(tag_pattern, content)
        if tag:
            tag_line = tag.group()
            tag_line = markdown_to_slack_link(tag_line.strip())
        else:
            tag_line = "No tag found"
        # add tag number and link
        slack_blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": "✨" + tag_line.lstrip("# ") + "✨"},
        })
        slack_blocks.append({"type": "divider"})
        slack_blocks.append({"type": "divider"})

        # Find sections within the version content
        sections = re.findall(r"(## .+?\n\n)(.+?)(?=\n## |$)", content, re.DOTALL)
        for section_header, section_content in sections:
            # Add section header to Slack blocks
            section_text = markdown_to_slack_link(section_header.lstrip("## ").strip())
            slack_blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*{}*".format(section_text)},
            })

            # Add section content, converting links to Slack format
            section_items = markdown_to_slack_link(section_content.strip())
            # replace a new line that is not followed by a - with a new line and a \t
            # to better show new lines inside the same commit
            section_items = re.sub(r"\n(?!\s*-)", "\n\t", section_items)
            # replce all - at the beginning or after a new line with ▷ 
            section_items = re.sub(r"^\s*-\s*", "▷ ", section_items, flags=re.MULTILINE)

            slack_blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": section_items},
            })
            # section_items_list = [
            #     f'▷ {(el.strip().lstrip("- "))}' for el in section_items.split("\n- ") if el.strip()
            # ]
            # for section_item in section_items_list:
            #     slack_blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": section_item}})
                # slack_blocks.append({"type": "divider"})
            slack_blocks.append({"type": "divider"})

    out = {
        "text": "Changelog...",
        "blocks": slack_blocks
    }
    return out


def main():
    changelog_path = sys.argv[1]  # Read the changelog string passed as a command-line argument
    with open(changelog_path, "r") as f:
        changelog_content = f.read()
        formatted_data = format_changelog_for_slack(changelog_content)
        print(json.dumps(formatted_data))  # Print the JSON output so it can be captured or redirected


changelog_content = """
# Changelog

# [1.3.0](https://github.com/altacucina/backend/compare/1.2...1.3.0) - (2024-03-07)

## <!-- 7 -->⚙️ Miscellaneous Tasks

- Comment ([f477451](https://github.com/altacucina/backend/commit/f47745117eb9f1d3d31abe395a39a50100f21272))  - (=)

## <!-- 0 -->🚀 Features

- **collection-admin:** Show username in list display [skip test] ([6d9a498](https://github.com/altacucina/backend/commit/6d9a498054148fb9a8cec92ddc6e04e37cd00550))  - (=)
- **admin:** Add id fields [skip test] ([c3a4af5](https://github.com/altacucina/backend/commit/c3a4af577fde50d89e20fb5360d83dbfb6e32b45))  - (Diego Margoni)
- **search:** Exclude banned users ([#3136](https://github.com/altacucina/backend/issues/3136)) ([90fd46f](https://github.com/altacucina/backend/commit/90fd46f30927a7d017723efe9378390254987fbc))  - (Diego Margoni)

## <!-- 1 -->🐛 Bug Fixes

- **ingredient:** Also accept json as unit on update-create ([3df6112](https://github.com/altacucina/backend/commit/3df6112b2a47daa6dc6a054210844d233caa0eaf))  - (=)
- Sponsorhisp admin recipe backlink [skip test] ([e2ca8d4](https://github.com/altacucina/backend/commit/e2ca8d4f1c86068f3eafa9893fa65315fa0a14f0))  - (=)
- **recipe-analytics:** Expose monthly_hitst field [skip test] ([b05e32f](https://github.com/altacucina/backend/commit/b05e32fdb61f9a559f0fed03a5a7f2a5df327895))  - (=)
- Prevent racing of requests ([687f6cc](https://github.com/altacucina/backend/commit/687f6cc4ac356ed10d8dd49ce21717f462639d4e))  - (=)
Introduce a request id and a reference to latest request. Dismiss
incoming responses other than from latest request https://altacucina.sentry.io/issues/

Remove timeouts which were used to mitigate the racing issue but are
obsolete now.
- **steps:** Creation order is decided by array position ([44746f3](https://github.com/altacucina/backend/commit/44746f31d49a6baf38cfb8d5c9fd8a4bd9de0ac2))  - (=)

<!-- generated by git-cliff -->

"""


def test_main():
    out = format_changelog_for_slack(changelog_content)
    assert out == {
        "blocks": [
            {"type": "header", "text": {"type": "plain_text", "text": "📝 Changelog"}},
            {"type": "divider"},
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "✨<https://github.com/altacucina/backend/compare/1.2...1.3.0|1.3.0> - (2024-03-07)✨",
                },
            },
            {"type": "divider"},
            {"type": "divider"},
            {"type": "section", "text": {"type": "mrkdwn", "text": "*⚙️ Miscellaneous Tasks*"}},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "▷ Comment (<https://github.com/altacucina/backend/commit/f47745117eb9f1d3d31abe395a39a50100f21272|f477451>)",
                },
            },
            {"type": "divider"},
            {"type": "divider"},
            {"type": "section", "text": {"type": "mrkdwn", "text": "*🚀 Features*"}},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "▷ *collection-admin:* Show username in list display <https://github.com/altacucina/backend/commit/6d9a498054148fb9a8cec92ddc6e04e37cd00550|skip test] ([6d9a498>)",
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "▷ *admin:* Add id fields <https://github.com/altacucina/backend/commit/c3a4af577fde50d89e20fb5360d83dbfb6e32b45|skip test] ([c3a4af5>)  - (Diego Margoni)",
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "▷ *search:* Exclude banned users (<https://github.com/altacucina/backend/issues/3136|#3136>) (<https://github.com/altacucina/backend/commit/90fd46f30927a7d017723efe9378390254987fbc|90fd46f>)  - (Diego Margoni)",
                },
            },
            {"type": "divider"},
            {"type": "divider"},
            {"type": "section", "text": {"type": "mrkdwn", "text": "*🐛 Bug Fixes*"}},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "▷ *ingredient:* Also accept json as unit on update-create (<https://github.com/altacucina/backend/commit/3df6112b2a47daa6dc6a054210844d233caa0eaf|3df6112>)",
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "▷ Sponsorhisp admin recipe backlink <https://github.com/altacucina/backend/commit/e2ca8d4f1c86068f3eafa9893fa65315fa0a14f0|skip test] ([e2ca8d4>)",
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "▷ *recipe-analytics:* Expose monthly_hitst field <https://github.com/altacucina/backend/commit/b05e32fdb61f9a559f0fed03a5a7f2a5df327895|skip test] ([b05e32f>)",
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "▷ Prevent racing of requests (<https://github.com/altacucina/backend/commit/687f6cc4ac356ed10d8dd49ce21717f462639d4e|687f6cc>) \nIntroduce a request id and a reference to latest request. Dismiss\nincoming responses other than from latest request https://altacucina.sentry.io/issues/\n\nRemove timeouts which were used to mitigate the racing issue but are\nobsolete now.",
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "▷ *steps:* Creation order is decided by array position (<https://github.com/altacucina/backend/commit/44746f31d49a6baf38cfb8d5c9fd8a4bd9de0ac2|44746f3>)",
                },
            },
            {"type": "divider"},
            {"type": "divider"},
        ]
    }


if __name__ == "__main__":
    main()
