## Backend Details


### The backend app consists of the following modules:

**core**:

This module is the core part of the backend app containing cloud, delta, and iceberg modules. Cloud modules contain functions to sign the cloud storage files (GCFs, S3,adls) with the specified expiration. Delta and Iceberg modules contain functions and classes to get the metadata and data files from lakehouse table formats and sign the data files using the cloud module and return the data in a protocol-compliant way.

**DB**:

This module contains tables, and queries needed for storing & querying the Framework’s metadata-RDS of the lakehouse-sharing server.

**routers**:

This module contains FastAPI routers for /admin, /auth,/delta-sharing.

**Securities**:

 This module implements JWT token generations.

**Utilities**:

 This module contains validators, exceptions, and pagination utility

**models**:

Contains request and response Pydantic models which fast API loves and integrates well.
