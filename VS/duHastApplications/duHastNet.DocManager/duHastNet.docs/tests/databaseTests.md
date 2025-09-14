Tests should be ORM-first and demonstrate sqlite-net-pcl's ORM capabilities:

When to Use Raw SQL:
Raw SQL should only be used when ORM can't handle the requirement:

Complex aggregations or window functions
Database-specific optimizations
Schema operations (CREATE INDEX, etc.)
Statistical queries not supported by LINQ

Your Architecture is Now:
Primary: sqlite-net-pcl ORM methods (InsertAsync, Table<T>().Where(), etc.)
Secondary: Raw SQL methods only when ORM limitations require it
Never: Bypassing sqlite-net-pcl entirely
This approach gives you the best of both worlds - the productivity and type safety of the ORM, with the fallback to raw SQL only when absolutely needed!