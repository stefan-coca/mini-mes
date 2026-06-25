```mermaid
stateDiagram-v2
    [*] --> STOPPED

    STOPPED --> RUNNING : piece
    RUNNING --> FAULT : timeout / fault
    FAULT --> RUNNING : fault reset
```