@csrf_exempt
def checkout(request):
    if request.method == 'POST':

        partner_id = request.GET.get('partner_id')

        cart_ids_param = request.GET.get('cart_ids')
        # cart_ids = [int(cart_id) for cart_id in cart_ids_param.strip('[]').split(',')]
        cart_ids = [int(cart_id) if cart_id else 0 for cart_id in cart_ids_param.strip('[]').split(',')]
        selected_items = DroneSales.objects.filter(user_id=partner_id, id__in=cart_ids)
        print(selected_items, "sssssssssssssssss")

        selected_cart_ids_param = request.GET.get('selected_cart_ids')

        cart_items = DroneSales.objects.filter(user_id=partner_id)

        if cart_ids_param:
            try:
                cart_ids = [int(cart_id) for cart_id in cart_ids_param.strip('[]').split(',')]
                cart_items = cart_items.filter(id__in=cart_ids)
                # selected_items = DroneSales.objects.filter(user_id=partner_id, id__in=cart_ids)
            except ValueError:
                return JsonResponse({'message': 'Invalid cart_ids parameter'}, status=400)

        # selected_items = DroneSales.objects.filter(user_id=partner_id,id__in=cart_ids_param)

        if selected_cart_ids_param:
            try:
                selected_cart_ids = [int(cart_id) for cart_id in selected_cart_ids_param.strip('[]').split(',')]
                selected_items = selected_items.filter(id__in=selected_cart_ids)
            except ValueError:
                return JsonResponse({'message': 'Invalid selected_cart_ids parameter'}, status=400)

        # all_items = cart_items.union(selected_items)

        total_amount = sum(
            (float(item.drone_id.our_price) if item.drone_id.our_price else 0)
            * item.quantity
            for item in selected_items
        )

        customizable_price = CustomizablePrice.objects.first()
        if customizable_price:
            paid_amount = float(customizable_price.custom_amount)
        else:
            return JsonResponse({'message': 'CustomizablePrice is not available.'}, status=400)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({'amount': int(paid_amount * 100), 'currency': 'INR'})

        request.session['razorpay_order_id'] = razorpay_order['id']
        request.session['total_amount'] = paid_amount

        for item in selected_items:
            user_instance = CustomUser.objects.get(id=partner_id)
            drone_sales_entry = DroneSales.objects.get(id=item.id)
            quantity = drone_sales_entry.quantity

            Order.objects.create(
                amount=(
                    float(item.drone_id.our_price) if item.drone_id.our_price else 0
                ),
                # order_status=None,
                order_status=Status.objects.get(status_name='Failure'), order_id=razorpay_order['id'],
                drone_id=item.drone_id,
                user_id=user_instance,
                created_date_time=datetime.now(),
                updated_date_time=datetime.now(),
                quantity=quantity,
            )

        response_data = {
            'order_id': razorpay_order['id'],
            'partner_id': partner_id,
            'total_amount': paid_amount,
            'our_price': float(total_amount),
        }

        return JsonResponse(response_data)

    return JsonResponse({'message': 'Invalid request method'}, status=405)


@csrf_exempt
def paymenthandler(request):
    if request.method == "POST":
        try:
            # Parse the JSON data from the request body
            json_data = json.loads(request.body.decode('utf-8'))

            payment_id = json_data.get('razorpay_payment_id')
            razorpay_order_id = json_data.get('razorpay_order_id')
            signature = json_data.get('razorpay_signature')

            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            result = razorpay_client.utility.verify_payment_signature(params_dict)

            # Handle the result as needed.
            if result:
                try:
                    # Get all orders with the specified razorpay_order_id
                    order_instances = Order.objects.filter(order_id=razorpay_order_id)

                    if order_instances.exists():
                        # Iterate through each order and update status, payment details, and delete from cart
                        for order_instance in order_instances:
                            order_instance.order_status = Status.objects.get(status_name='Pending')
                            order_instance.payment_id = payment_id
                            order_instance.razorpay_signature = signature

                            # Fetch quantity from DroneSales
                            drone_sales_entries = DroneSales.objects.filter(
                                drone_id=order_instance.drone_id, user=order_instance.user_id
                            )

                            # Update quantity in the Order table
                            if drone_sales_entries.exists():
                                order_instance.quantity = drone_sales_entries[0].quantity

                            order_instance.save()

                            # Delete the entry from Dronesales table
                            cart = DroneSales.objects.filter(drone_id=order_instance.drone_id,
                                                             user_id=order_instance.user_id)
                            cart.delete()
                    else:
                        return JsonResponse({"message": "Orders not found"}, status=404)

                    return JsonResponse({"message": "Payment completed successfully"}, status=200)

                except Order.DoesNotExist:
                    return JsonResponse({"message": "Orders not found"}, status=404)

            else:
                # If signature verification fails.
                raise SignatureVerificationError("Razorpay Signature Verification Failed")

        except SignatureVerificationError as e:
            return JsonResponse({"message": f"Signature Verification Error: {str(e)}"}, status=400)

        except ValidationError as e:
            return JsonResponse({"message": f"Validation Error: {str(e)}"}, status=400)

        except Exception as e:
            return JsonResponse({"message": f"Error: {str(e)}"}, status=500)

    else:
        return JsonResponse({"message": "Invalid request method. Only POST requests are allowed."}, status=405)