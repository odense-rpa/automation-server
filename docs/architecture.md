This is the current backend architecture. It has over time become a rather big mess and will be cleaned up in the future.

```mermaid

graph TD

    subgraph Backend
        C[REST API]
        E[Worker]
        G[Repository / Service mix]
        F[SQLModel]
        H[SQLite3]
        C --> G
        E --> G
        G --> F
        F --> H
    end

```

Currently we are aiming for an implementation that will look more like this.

```mermaid

graph TD
    subgraph Clients
        A[Frontend]
        E[Worker]
    end
    subgraph Backend
        C[REST API]
        G[Services]
        F[Repositories/ UOW]
        H[SQLite3]
        C --> G
        G --> F
        F --> H
    end

    E -->|REST| C
    A -->|REST| C
```
