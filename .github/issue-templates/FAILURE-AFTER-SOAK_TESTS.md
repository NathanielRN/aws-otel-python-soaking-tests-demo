---
title: Performance Threshold breached AFTER Soak Tests completed for the ({{ env.APP_PLATFORM }}, {{ env.INSTRUMENTATION_TYPE }}) Sample App
# assignees: open-telemetry/opentelemetry-<LANGUAGE>-approvers
labels: bug, enhancement
---
# Description

After the Soak Tests completed, a performance degradation was revealed for commit {{ sha }} of the `{{ ref }}` branch for the ({{ env.APP_PLATFORM }}, {{ env.INSTRUMENTATION_TYPE }}) Sample App. Check out the Action Logs from the `{{ workflow }}` [workflow run on GitHub]({{ env.GITHUB_SERVER_URL }}/{{ env.GITHUB_REPOSITORY }}/actions/runs/{{ env.GITHUB_RUN_ID }}) to view the threshold violation.

More: {{ repo }}
More: {{ repo.repo }}
More: {{ repo.owner }}

More: {{ issue }}

Test GitHub context 1: {{ github.context }}
Test GitHub context 1 repo owner: {{ github.context.repo.owner }}
Test GitHub context 1 repo repo: {{ github.context.repo.repo }}
Test GitHub context 1 ref: {{ github.context.ref }}
Test GitHub context 1 ref issue owner: {{ github.context.issue.owner }}
Test GitHub context 1 ref issue repo: {{ github.context.issue.repo }}
Test GitHub context 1 ref issue issue_number: {{ github.context.issue.issue_number }}
Test GitHub context 1 ref pullRequest owner: {{ github.context.pullRequest.owner }}
Test GitHub context 1 ref pullRequest repo: {{ github.context.pullRequest.repo }}
Test GitHub context 1 ref pullRequest pull_number: {{ github.context.pullRequest.pull_number }}

Test GitHub context 2: {{ context }}
Test GitHub context 2 repo owner: {{ context.repo.owner }}
Test GitHub context 2 repo repo: {{ context.repo.repo }}
Test GitHub context 2 ref: {{ context.ref }}
Test GitHub context 2 ref issue owner: {{ context.issue.owner }}
Test GitHub context 2 ref issue repo: {{ context.issue.repo }}
Test GitHub context 2 ref issue issue_number: {{ context.issue.issue_number }}
Test GitHub context 2 ref pullRequest owner: {{ context.pullRequest.owner }}
Test GitHub context 2 ref pullRequest repo: {{ context.pullRequest.repo }}
Test GitHub context 2 ref pullRequest pull_number: {{ context.pullRequest.pull_number }}

Test: {{ github.context.repository }}
Test: {{ github.context.repository.repo }}
Test: {{ github.context.repository.owner }}
Test: {{ github.context.repository.repository }}

Test: {{ github.repository }}
Test: {{ github.repository.repo }}
Test: {{ github.repository.owner }}
Test: {{ github.repository.repository }}

Test: {{ context.repository }}
Test: {{ context.repository.repo }}
Test: {{ context.repository.owner }}
Test: {{ context.repository.repository }}

Test: {{ repository }}
Test: {{ repository.repo }}
Test: {{ repository.owner }}
Test: {{ repository.repository }}

Test: {{ repository_owner }}
Test: {{ github.repository_owner }}

# Useful Links

Snapshots of the Soak Test run are available [on the gh-pages branch](https://github.com/{{ env.GITHUB_REPOSITORY }}/tree/gh-pages/soak-tests/snapshots). These are the snapshots for the violating commit:

![CPU Load Soak Test SnapShot Image](https://github.com/{{ env.GITHUB_REPOSITORY }}/blob/gh-pages/soak-tests/snapshots/{{ sha }}/{{ env.APP_PLATFORM }}-{{ env.INSTRUMENTATION_TYPE }}-cpu-load-soak-{{ env.GITHUB_RUN_ID }}.png?raw=true)
![Total Memory Soak Test SnapShot Image](https://github.com/{{ env.GITHUB_REPOSITORY }}/blob/gh-pages/soak-tests/snapshots/{{ sha }}/{{ env.APP_PLATFORM }}-{{ env.INSTRUMENTATION_TYPE }}-total-memory-soak-{{ env.GITHUB_RUN_ID }}.png?raw=true)

The threshold violation should also be noticeable on [our graph of Soak Test average results per commit](https://{{ env.GITHUB_REPOSITORY_OWNER }}.github.io/{{ env.GITHUB_REPOSITORY_NAME }}/soak-tests/per-commit-overall-results/index.html).
