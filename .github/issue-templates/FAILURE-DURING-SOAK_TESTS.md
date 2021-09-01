---
title: Performance Threshold breached during Soak Tests execution
assignees: NathanielRN
labels: bug, enhancement
---
During the Soak Tests execution, a performance degradation was revealed for {{ tools.context.ref }} on commit {{ tools.context.sha }}. Check out the Action Logs to view the threshold violation.

Also check out:

CONTEXT ACTOR - {{ tools.context.actor }}
CONTEXT EVENT - {{ tools.context.event }}
CONTEXT PAYLOAD - {{ tools.context.payload }}
CONTEXT WORKFLOW - {{ tools.context.workflow }}