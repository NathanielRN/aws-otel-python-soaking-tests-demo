---
title: Performance Threshold breached after Soak Tests completed
assignees: NathanielRN
labels: bug, enhancement
---
After the Soak Tests completed, a performance degradation was revealed for {{ tools.context.ref }} on commit {{ tools.context.sha }}. Check out the Action Logs to view the threshold violation.

Also check out:

CONTEXT ACTOR - {{ tools.context.actor }}
CONTEXT EVENT - {{ tools.context.event }}
CONTEXT PAYLOAD - {{ tools.context.payload }}
CONTEXT WORKFLOW - {{ tools.context.workflow }}