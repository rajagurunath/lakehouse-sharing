ListShareResult = [
    {"id": "1ff31536-3777-404e-bf55-8c4dd2551029", "name": "delta_share1"},
    {"id": "183c7152-4ef8-40f0-9fa2-87eb4917ed03", "name": "delta_share2"},
    {"id": "ab4eebbc-93e2-4217-b641-4189b354edc0", "name": "delta_share3"},
    {"id": "9fb26f71-db34-4a9d-bb4f-0ec87ad2b1f1", "name": "iceberg_share"},
]

ShareResult = {"id": "1ff31536-3777-404e-bf55-8c4dd2551029", "name": "delta_share1"}

ListSchemaResult = [
    {"name": "delta_schema", "share": "delta_share1"},
    {"name": "delta_schema1", "share": "delta_share1"},
]

ListTableResult = [
    {
        "name": "iceberg_benchmark_nyc_taxi_trips_v2",
        "schema": "tripsdb",
        "share": "iceberg_share",
        "shareId": "9fb26f71-db34-4a9d-bb4f-0ec87ad2b1f1",
        "id": "8202f214-af87-40aa-aed9-6f4e7a66fe47",
    }
]

ListAllTableResult = [
    {
        "name": "test_hm",
        "schema": "schema2",
        "share": "delta_share2",
        "shareId": "183c7152-4ef8-40f0-9fa2-87eb4917ed03",
        "id": "1cea2311-49d6-4741-8bce-aa785974d9cb",
    },
    {
        "name": "test_hm",
        "schema": "schema2",
        "share": "delta_share2",
        "shareId": "183c7152-4ef8-40f0-9fa2-87eb4917ed03",
        "id": "1cea2311-49d6-4741-8bce-aa785974d9cb",
    },
]
