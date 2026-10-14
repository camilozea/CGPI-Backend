from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with engine.begin() as conn:
        def add_role_column(sync_conn):
            from sqlalchemy import inspect, text
            inspector = inspect(sync_conn)
            columns = [c["name"] for c in inspector.get_columns("users")]
            if "role" not in columns:
                sync_conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user'"))

            has_admin = sync_conn.execute(
                text("SELECT COUNT(*) FROM users WHERE role = 'admin'")
            ).scalar() > 0

            if not has_admin:
                first_user = sync_conn.execute(
                    text("SELECT id FROM users ORDER BY id LIMIT 1")
                ).scalar()
                if first_user:
                    sync_conn.execute(
                        text("UPDATE users SET role = 'admin' WHERE id = :uid"),
                        {"uid": first_user},
                    )
                    print(f"Usuario {first_user} promovido a administrador")

            if "active" not in columns:
                sync_conn.execute(text("ALTER TABLE users ADD COLUMN active BOOLEAN NOT NULL DEFAULT 1"))
                print("Columna 'active' agregada a users")

            if "business_id" not in columns:
                sync_conn.execute(text("ALTER TABLE users ADD COLUMN business_id INTEGER DEFAULT NULL"))
                print("Columna 'business_id' agregada a users")

            if "created_at" not in columns:
                sync_conn.execute(text("ALTER TABLE users ADD COLUMN created_at TIMESTAMP"))
                print("Columna 'created_at' agregada a users")

            for table, col in [("sales", "user_id"), ("returns", "user_id")]:
                cols = [c["name"] for c in inspector.get_columns(table)]
                if col not in cols:
                    sync_conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} INTEGER NOT NULL DEFAULT 0"))
                    print(f"Columna '{col}' agregada a {table}")
        await conn.run_sync(add_role_column)

    async with engine.begin() as conn:
        def migrate_products(sync_conn):
            from sqlalchemy import inspect, text
            inspector = inspect(sync_conn)
            columns = [c["name"] for c in inspector.get_columns("products")]

            if "Price_mayor" not in columns or "Price_cliente" not in columns:
                if "Price_mayor" not in columns:
                    sync_conn.execute(text("ALTER TABLE products ADD COLUMN Price_mayor FLOAT NOT NULL DEFAULT 0"))
                    print("Columna 'Price_mayor' agregada a products")
                if "Price_cliente" not in columns:
                    sync_conn.execute(text("ALTER TABLE products ADD COLUMN Price_cliente FLOAT NOT NULL DEFAULT 0"))
                    print("Columna 'Price_cliente' agregada a products")
                    sync_conn.execute(text("UPDATE products SET Price_cliente = Price WHERE Price_cliente = 0"))
                    print("Datos migrados de Price a Price_cliente")

            if "Price" in columns:
                sync_conn.execute(text("""
                    CREATE TABLE products_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name_product VARCHAR(200) NOT NULL,
                        Marca VARCHAR(100) NOT NULL,
                        Tipo VARCHAR(50),
                        Description VARCHAR(500),
                        Price_mayor FLOAT NOT NULL DEFAULT 0,
                        Price_cliente FLOAT NOT NULL DEFAULT 0,
                        cantidad INTEGER NOT NULL DEFAULT 0
                    )
                """))
                sync_conn.execute(text("""
                    INSERT INTO products_new (id, name_product, Marca, Tipo, Description, Price_mayor, Price_cliente, cantidad)
                    SELECT id, name_product, Marca, Tipo, Description, Price_mayor, Price_cliente, cantidad FROM products
                """))
                sync_conn.execute(text("DROP TABLE products"))
                sync_conn.execute(text("ALTER TABLE products_new RENAME TO products"))
                print("Columna 'Price' eliminada de products (migrada a Price_mayor / Price_cliente)")
        await conn.run_sync(migrate_products)

    async with engine.begin() as conn:
        def migrate_sales(sync_conn):
            from sqlalchemy import inspect, text
            inspector = inspect(sync_conn)
            cols = [c["name"] for c in inspector.get_columns("sales")]
            if "documento" not in cols:
                sync_conn.execute(text("ALTER TABLE sales ADD COLUMN documento VARCHAR(50) DEFAULT NULL"))
                print("Columna 'documento' agregada a sales")
            if "discount_prise" not in cols:
                sync_conn.execute(text("ALTER TABLE sales ADD COLUMN discount_prise FLOAT DEFAULT NULL"))
                print("Columna 'discount_prise' agregada a sales")
        await conn.run_sync(migrate_sales)

    async with engine.begin() as conn:
        def migrate_businesses(sync_conn):
            from sqlalchemy import inspect, text
            inspector = inspect(sync_conn)
            cols = [c["name"] for c in inspector.get_columns("businesses")]
            if "profit_margin" not in cols:
                sync_conn.execute(text("ALTER TABLE businesses ADD COLUMN profit_margin INTEGER NOT NULL DEFAULT 30"))
                print("Columna 'profit_margin' agregada a businesses")
        await conn.run_sync(migrate_businesses)

    async with engine.begin() as conn:
        def migrate_daily_goals(sync_conn):
            from sqlalchemy import inspect, text
            inspector = inspect(sync_conn)
            cols = [c["name"] for c in inspector.get_columns("daily_goals")]
            if "business_id" not in cols:
                sync_conn.execute(text("ALTER TABLE daily_goals ADD COLUMN business_id INTEGER DEFAULT NULL"))
                print("Columna 'business_id' agregada a daily_goals")
        await conn.run_sync(migrate_daily_goals)

    async with engine.begin() as conn:
        def migrate_businesses_v2(sync_conn):
            from sqlalchemy import inspect, text
            inspector = inspect(sync_conn)
            cols = [c["name"] for c in inspector.get_columns("businesses")]
            if "type" not in cols:
                sync_conn.execute(text("ALTER TABLE businesses ADD COLUMN type VARCHAR(20) NOT NULL DEFAULT 'ventas'"))
                print("Columna 'type' agregada a businesses")
            if "subcategories" not in cols:
                sync_conn.execute(text("ALTER TABLE businesses ADD COLUMN subcategories TEXT DEFAULT NULL"))
                print("Columna 'subcategories' agregada a businesses")
        await conn.run_sync(migrate_businesses_v2)

    async with engine.begin() as conn:
        def migrate_businesses_v3(sync_conn):
            from sqlalchemy import inspect, text
            inspector = inspect(sync_conn)
            cols = [c["name"] for c in inspector.get_columns("businesses")]
            if "nit" not in cols:
                sync_conn.execute(text("ALTER TABLE businesses ADD COLUMN nit VARCHAR(50) DEFAULT NULL"))
                print("Columna 'nit' agregada a businesses")
        await conn.run_sync(migrate_businesses_v3)

    async with engine.begin() as conn:
        def migrate_repairs(sync_conn):
            from sqlalchemy import inspect, text
            inspector = inspect(sync_conn)
            tables = inspector.get_table_names()
            needs_rebuild = False
            if "repairs" in tables:
                cols = [c["name"] for c in inspector.get_columns("repairs")]
                if "auto" not in cols:
                    needs_rebuild = True
            if needs_rebuild:
                sync_conn.execute(text("DROP TABLE IF EXISTS repair_parts"))
                sync_conn.execute(text("DROP TABLE IF EXISTS repairs"))
                tables = []
            if "repairs" not in tables:
                sync_conn.execute(text("""
                    CREATE TABLE repairs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        auto VARCHAR(200) NOT NULL,
                        marca VARCHAR(200) NOT NULL,
                        modelo VARCHAR(100) NOT NULL,
                        nombres VARCHAR(200) NOT NULL,
                        apellidos VARCHAR(200) NOT NULL,
                        tipo_documento VARCHAR(20) NOT NULL DEFAULT 'CC',
                        numero_documento VARCHAR(50) NOT NULL,
                        tipo_reparacion VARCHAR(200) NOT NULL,
                        descripcion TEXT,
                        fotos TEXT,
                        fecha_entrega DATE NOT NULL,
                        estado VARCHAR(30) NOT NULL DEFAULT 'pendiente',
                        created_at TIMESTAMP,
                        user_id INTEGER NOT NULL DEFAULT 0
                    )
                """))
                print("Tabla 'repairs' creada")
            if "repairs" in tables:
                cols = [c["name"] for c in inspector.get_columns("repairs")]
                if "costo" not in cols:
                    sync_conn.execute(text("ALTER TABLE repairs ADD COLUMN costo FLOAT NOT NULL DEFAULT 0"))
                    print("Columna 'costo' agregada a repairs")
                if "metodo_pago" not in cols:
                    sync_conn.execute(text("ALTER TABLE repairs ADD COLUMN metodo_pago VARCHAR(50) DEFAULT NULL"))
                    print("Columna 'metodo_pago' agregada a repairs")

            if "repair_parts" not in tables:
                sync_conn.execute(text("""
                    CREATE TABLE repair_parts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre VARCHAR(200) NOT NULL,
                        cantidad INTEGER NOT NULL DEFAULT 0,
                        precio_costo FLOAT NOT NULL DEFAULT 0,
                        precio_venta FLOAT NOT NULL DEFAULT 0,
                        proveedor VARCHAR(200),
                        created_at TIMESTAMP,
                        user_id INTEGER NOT NULL DEFAULT 0
                    )
                """))
                print("Tabla 'repair_parts' creada")
        await conn.run_sync(migrate_repairs)

    async with engine.begin() as conn:
        def migrate_quotes(sync_conn):
            from sqlalchemy import inspect, text
            if "quotes" not in inspect(sync_conn).get_table_names():
                sync_conn.execute(text("""
                    CREATE TABLE quotes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        auto VARCHAR(200) NOT NULL,
                        marca VARCHAR(200) NOT NULL,
                        modelo VARCHAR(100) NOT NULL,
                        nombres VARCHAR(200) NOT NULL,
                        apellidos VARCHAR(200) NOT NULL,
                        tipo_documento VARCHAR(20) NOT NULL DEFAULT 'CC',
                        numero_documento VARCHAR(50) NOT NULL,
                        tipo_reparacion VARCHAR(200) NOT NULL,
                        descripcion TEXT,
                        items TEXT DEFAULT '[]',
                        total FLOAT NOT NULL DEFAULT 0,
                        validez_dias INTEGER NOT NULL DEFAULT 15,
                        notas TEXT,
                        estado VARCHAR(30) NOT NULL DEFAULT 'pendiente',
                        created_at TIMESTAMP,
                        user_id INTEGER NOT NULL DEFAULT 0
                    )
                """))
                print("Tabla 'quotes' creada")
        await conn.run_sync(migrate_quotes)
