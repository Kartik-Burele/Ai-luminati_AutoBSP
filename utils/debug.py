def print_diff(diff):

    print("=" * 80)
    print(diff.filename)
    print("=" * 80)

    print("\nVendor")

    for c in diff.vendor_changes:
        print(c)

    print("\nCustomer")

    for c in diff.customer_changes:
        print(c)