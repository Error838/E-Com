from rest_framework import viewsets
from .models import User, Product, Order, CartItem, OrderItem
from .serializers import UserSerializer, ProductSerializer, OrderSerializer, UserRegistrationSerializer, CartItemSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

@api_view(['GET'])
def get_available_products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({'message': 'Registration successful.'}, status=201)
    return Response(serializer.errors, status=400)

@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)

    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=200)
    return Response({'message': 'Invalid credentials'}, status=401)

@api_view(['POST'])
def add_to_cart(request):
    user = request.user
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity')

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'message': 'Product does not exist.'}, status=400)

    # Implement logic to add the product to the user's cart
    cart_item = CartItem.objects.create(user=user, product=product, quantity=quantity)

    serializer = CartItemSerializer(cart_item)
    return Response(serializer.data, status=201)


@api_view(['POST'])
def update_cart(request):
    user = request.user
    cart_item_id = request.data.get('cart_item_id')
    quantity = request.data.get('quantity')

    try:
        cart_item = CartItem.objects.get(id=cart_item_id, user=user)
    except CartItem.DoesNotExist:
        return Response({'message': 'Cart item does not exist.'}, status=400)

    # Update the quantity of the cart item
    cart_item.quantity = quantity
    cart_item.save()

    serializer = CartItemSerializer(cart_item)
    return Response(serializer.data, status=200)


@api_view(['POST'])
def remove_from_cart(request):
    user = request.user
    cart_item_id = request.data.get('cart_item_id')

    try:
        cart_item = CartItem.objects.get(id=cart_item_id, user=user)
    except CartItem.DoesNotExist:
        return Response({'message': 'Cart item does not exist.'}, status=400)

    # Remove the cart item from the user's cart
    cart_item.delete()

    return Response({'message': 'Cart item removed successfully.'}, status=200)


@api_view(['POST'])
def place_order(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)

    if not cart_items:
        return Response({'message': 'Cart is empty.'}, status=400)

    # Create a new order for the user
    order = Order.objects.create(user=user)

    # Add the cart items to the order
    for cart_item in cart_items:
        order_item = OrderItem.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity)

    # Clear the user's cart
    cart_items.delete()

    serializer = OrderSerializer(order)
    return Response(serializer.data, status=201)

@api_view(['GET'])
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)
