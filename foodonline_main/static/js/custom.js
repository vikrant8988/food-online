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
            response.cart_amount
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
            response.cart_amount
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
            response.cart_amount
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
  function applyCartAmount(cart_amount){
    if (window.location.pathname == '/cart/'){
      $('#subtotal').html(cart_amount['subtotal'])
      console.log(cart_amount);
      cart_amount['tax_details'].forEach(tax => {
        $('#tax-'+tax.type)?.html(tax.amount)
        console.log(`${tax.type} - ${tax.amount}`);
      })
      $('#grand_total').html(cart_amount['grand_total'])
    }
  }


  // place the cart item quantity on load
  $('.item-qty').each(function(){
    var the_id = $(this).attr('id')
    var qty = $(this).attr('data-qty')
    $('#'+the_id).html(qty)
  })

  // opening hours
  $('#opening-hours').on('submit', function(e){
    e.preventDefault();

    const formData = new FormData(this);
    const form = this;

    for (let [key, value] of formData.entries()) {
      console.log(key + ": " + value);
    }

  const isClosed = formData.has('is_closed');
  formData.set('is_closed', isClosed ? 'True' : 'False');

  const isValid = formData.get('day') && (isClosed || (formData.get('from_hour') && formData.get('to_hour')));

  if (isValid) {
    $.ajax({
      url: formData.get('add_hour_url'),
      method: 'POST',
      data: formData,
      processData: false,
      contentType: false,  
      success: function(response) {
        console.log(response)
        data = response.data
        html = `
          <tr id="hour-${data.id}">
            <td class="text-left">
              <b>${data.day}</b>
            </td>
            <td class="text-center">
            ${data.is_closed ? 'Closed' : `${data.from_hour} - ${data.to_hour}`}
            </td>
            <td class="text-center">
              <a href="#" class="remove-hour" data-url="/vendor/opening-hours/delete/${data.id}">Remove</a>
            </td>
          </tr>
        `
        document.getElementById('hour-'+data.id)?.remove()
        $('.opening_hours').append(html)
        swal(response.status, response.message, 'success');
        form.reset()
      },
      error: function(error) {
        const errorMessage = error.responseJSON ? error.responseJSON.message : 'An unexpected error occurred';
        swal('Error', errorMessage, 'error');
      }
    });

  } 
  else {
    swal('Please fill all fields', '', 'info');
  }
  });

  // remove opening hour
  $(document).on('click','.remove-hour', function(e){
    e.preventDefault();
    url = $(this).attr('data-url')

    $.ajax({
      type: 'GET',
      url: url,
      success: function(response){
        if(response.status == 'success'){
          document.getElementById('hour-'+response.id).remove()
        }
      }
    })
  });
  // document ready close
});

// setting search cordinates
function setCoordinate() {
  const location = $('#address').val().trim().split('-');
  const coordinate = location[1].trim().split(',');
  const address = location[0].trim();
  
  if (coordinate.length !== 2) {
    alert("Invalid coordinates! Please enter in format: latitude,longitude");
    return;
  }

  const lat = coordinate[0].trim();
  const long = coordinate[1].trim();

  $('#lat').val(lat);
  $('#long').val(long);
  $('#address').val(address);

  return true
}
