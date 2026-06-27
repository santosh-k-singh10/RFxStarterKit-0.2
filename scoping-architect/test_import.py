try:
    from gsc_template_api import router as gsc_router
    print('Import successful')
    print(f'Router prefix: {gsc_router.prefix}')
    print(f'Number of routes: {len(gsc_router.routes)}')
    for route in gsc_router.routes:
        print(f'  - {route.path}')
except Exception as e:
    import traceback
    print(f'Import failed: {e}')
    traceback.print_exc()

# Made with Bob
