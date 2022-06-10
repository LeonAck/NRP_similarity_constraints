from concurrent.futures import ThreadPoolExecutor, as_completed


def parallel(handler, args_list, *, max_workers=5):
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []

        for args in args_list:
            future = executor.submit(handler, *args)
            futures.append(future)

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

    return results
