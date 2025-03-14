$(document).ready(function(){
  // add to cart
  $('.add_to_cart').on('click', function(e){
    e.preventDefault();

    food_id = $(this).attr('data-id');
    url = $(this).attr('data-url');

    $.ajax({
      type: 'GET',
      url: url,
      success: function(response){
        if (response.status == 'login_required'){
          swal(response.message,"", "info").then(function(){
            window.location = '/login';
          })
        }
        else if(response.status == 'failed'){
          swal(response.message,"", "error")
        }
        else{
          $('#cart_counter').html(response.cart_counter['cart_count']);
          $('#qty-'+food_id).html(response.qty);

          //subtotal, tax and grand_total
          applyCartAmount(
            response.cart_amount['subtotal'],
            response.cart_amount['tax'],
            response.cart_amount['grand_total']
          )
        }
      }
    })

  })

  // decrease from cart
  $('.decrease_cart').on('click', function(e){
    e.preventDefault();

    food_id = $(this).attr('data-id')
    cart_id = $(this).attr('id')
    url = $(this).attr('data-url')

    $.ajax({
      type: 'GET',
      url: url,
      success: function(response){
        if (response.status == 'login_required'){
          swal(response.message,"", "info").then(function(){
            window.location = '/login';
          })
        }
        else if(response.status == 'failed'){
          swal(response.message,"", "error")
        }
        else{
          $('#cart_counter').html(response.cart_counter['cart_count']);
          $('#qty-'+food_id).html(response.qty);

          checkEmptyCart(response.cart_counter['cart_count'])
          removeCartItem(response.qty, cart_id)

          //subtotal, tax and grand_total
          applyCartAmount(
            response.cart_amount['subtotal'],
            response.cart_amount['tax'],
            response.cart_amount['grand_total']
          )
        }

      }
    })

  })

  // delete from cart
  $('.delete_cart').on('click', function(e){
    e.preventDefault();

    cart_id = $(this).attr('data-id')
    url = $(this).attr('data-url')

    $.ajax({
      type: 'GET',
      url: url,
      success: function(response){
        if(response.status == 'failed'){
          swal(response.message,"", "error")
        }
        else{
          $('#cart_counter').html(response.cart_counter['cart_count']);
          swal(response.status, response.message, "success")

          removeCartItem(0, cart_id)
          checkEmptyCart(response.cart_counter['cart_count'])

          //subtotal, tax and grand_total
          applyCartAmount(
            response.cart_amount['subtotal'],
            response.cart_amount['tax'],
            response.cart_amount['grand_total']
          )
        }

      }
    })

  })

  // delete the cart element if the qty is 0
  function removeCartItem(cartItemQty, cart_id){
    if (cartItemQty <= 0){
      document.getElementById('cart-item-'+cart_id)?.remove()
    }
  }

  // check if cart is empty
  function checkEmptyCart(cart_counter){
    if (cart_counter == 0){
      const emptyCart = document.getElementById('empty-cart');
      if (emptyCart) {
        emptyCart.style.display = 'block';
      }
    }
  }

  // apply cart amount
  function applyCartAmount(subtotal, tax, grand_total){
    if (window.location.pathname == '/cart/'){
      $('#subtotal').html(subtotal)
      $('#tax').html(tax)
      $('#grand_total').html(grand_total)
    }
  }


  // place the cart item quantity on load
  $('.item-qty').each(function(){
    var the_id = $(this).attr('id')
    var qty = $(this).attr('data-qty')
    $('#'+the_id).html(qty)
  })

});