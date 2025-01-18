class CreatePaymentView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # Your logic for creating the PayPal payment here
        # Example logic as described earlier
        cart_items = request.user.carts.all()
        subtotal = sum(Decimal(item.price) for item in cart_items)  # Using Decimal for precision

        items = []
        for item in cart_items:
            items.append({
                "name": item.item.name,
                "sku": str(item.item.id),
                "price": f"{item.item.price:.2f}",
                "currency": "USD",
                "quantity": item.quantity
            })

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "redirect_urls": {
                "return_url": request.build_absolute_uri("/payment/success/"),
                "cancel_url": request.build_absolute_uri("/payment/cancel/"),
            },
            "transactions": [{
                "item_list": {"items": items},
                "amount": {
                    "total": f"{subtotal:.2f}",
                    "currency": "USD"
                },
                "description": "Order from CAFE_DELISH"
            }]
        })

        if payment.create():
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = link.href
                    return redirect(approval_url)
        else:
            return render(request, "payment_error.html", {"error": payment.error})
            


class PaymentCancelView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "payment_cancel.html")
    

class PaymentSuccessView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        payment_id = request.GET.get("paymentId")
        payer_id = request.GET.get("PayerID")

        try:
            # Retrieve the payment from PayPal
            payment = paypalrestsdk.Payment.find(payment_id)

            # Execute the payment
            if payment.execute({"payer_id": payer_id}):
                # Fetch cart items before clearing
                cart_items = request.user.carts.all()

                # Create a transaction record
                transaction = Transaction.objects.create(
                    user=request.user,
                    payment_id=payment.id,
                    payer_id=payer_id,
                    amount=sum(cart_item.item.price * cart_item.quantity for cart_item in cart_items),
                    status=payment.state
                )

                # Create an order
                order = Order.objects.create(
                    user=request.user,
                    status="Completed"  # Set the default order status
                )

                total_amount = Decimal(0.0)

                # Populate the OrderItem table
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        menu_item=cart_item.item,  # Correct reference
                        quantity=cart_item.quantity,
                        price=cart_item.item.price * cart_item.quantity
                    )
                    total_amount += cart_item.item.price * cart_item.quantity
                order.total_amount = total_amount
                order.save()
                # Clear the user's cart after processing
                cart_items.delete()

                # Render the success page
                return render(request, "payment_success.html", {"transaction": transaction, "order": order})
            else:
                # Payment execution failed
                return render(request, "payment_error.html", {"error": payment.error})

        except Exception as e:
            # Catch any unexpected errors
            return render(request, "payment_error.html", {"error": str(e)})