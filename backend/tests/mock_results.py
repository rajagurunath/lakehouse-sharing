ListShareResult = [
    {"id": "01460171-de53-4eb6-8d99-a8ed491bac1d", "name": "iceberg_share"},
    {"id": "2b3b8cc2-cc46-4af5-9f59-92e7176e855a", "name": "delta_share1"},
    {"id": "78a3a3d6-afb0-49c9-a45d-c89777f3b885", "name": "delta_share2"},
    {"id": "97c9eeb6-2c18-481c-8690-40f0c819a2f2", "name": "delta_share3"},
]

ShareResult = {"id": "01460171-de53-4eb6-8d99-a8ed491bac1d", "name": "iceberg_share"}

ListSchemaResult = [
    {"name": "delta_schema", "share": "delta_share1"},
    {"name": "delta_schema1", "share": "delta_share1"},
]

ListTableResult = [
    {
        "name": "iceberg_benchmark_nyc_taxi_trips_v2",
        "schema": "tripsdb",
        "share": "iceberg_share",
        "shareId": "01460171-de53-4eb6-8d99-a8ed491bac1d",
        "id": "b22e0a03-7236-4482-9c6c-aed926073384",
    }
]

ListAllTableResult = [
    {
        "name": "test_hm",
        "schema": "schema2",
        "share": "delta_share2",
        "shareId": "78a3a3d6-afb0-49c9-a45d-c89777f3b885",
        "id": "c098e038-d032-4da5-b5f8-e7401073b04c",
    },
    {
        "name": "test_hm",
        "schema": "schema2",
        "share": "delta_share2",
        "shareId": "78a3a3d6-afb0-49c9-a45d-c89777f3b885",
        "id": "c098e038-d032-4da5-b5f8-e7401073b04c",
    },
]
