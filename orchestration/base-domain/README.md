# base-domain

## domains

### `base_domain.py` standardization

#### data flow -- core domain interfaces

```
domain.on_handle(<input>)

domain.on_handled(<_cb-for-output)
```

#### observability flow -- core domain monitoring interfaces

```
domain.on_completed(monitor.on_completed)

domain.on_error(monitor.on_error)
```
