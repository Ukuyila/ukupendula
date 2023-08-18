
paypal.Buttons({

 createSubscription: function(data, actions) {

   return actions.subscription.create({

    'plan_id': 'P-9ML82449EL4199549MRMNKDA' // Creates the Starter Plan subscription $9

    });

  },

  onApprove: function(data, actions) {

    // Webhook action to be moved to the view
    $.ajax({
      type: "POST",
      url: "{% url 'paypal-payment-success' %}",
      data: {
        'subscriptionId': data.subscriptionID,
        'subscriptionType': 'starter',
        'userId': "{{user.profile.uniqueId|safe}}",
        'csrfmiddlewaretoken': "{{csrf_token}}",
      },
      success: function (res) {
        if (res.result == 'SUCCESS') {
          alert('You have successfully subscribed to the Starter package.')
          setTimeout(() => {
            window.location.href='subscription-plans'
          }, 2000)
          
        } else {
          alert('Something went wrong, please try again later!')
          setTimeout(() => {
            window.location.href='subscription-plans'
          }, 2000)
        }
      }
    })

  },
  onCancel: function(data) {
    alert('You have cancelled your paypal payment transtaction :('); // when user cancels the transtaction
  }

}).render('#paypal-button-container1'); // Renders the PayPal button

paypal.Buttons({

  createSubscription: function(data, actions) {
 
    return actions.subscription.create({
 
      'plan_id': 'P-1C335947G15101630MRMNMWA' // Creates the Professional Plan subscription $19
 
    });
 
  },
 
  onApprove: function(data, actions) {
 
    // Webhook action to be moved to the view
    $.ajax({
      type: "POST",
      url: "{% url 'paypal-payment-success' %}",
      data: {
        'subscriptionId': data.subscriptionID,
        'subscriptionType': 'professional',
        'userId': "{{user.profile.uniqueId|safe}}",
        'csrfmiddlewaretoken': "{{csrf_token}}",
      },
      success: function (res) {
        if (res.result == 'SUCCESS') {
          alert('You have successfully subscribed to the Professional package.')
          setTimeout(() => {
            window.location.href='subscription-plans'
          }, 2000)
          
        } else {
          alert('Something went wrong, please try again later!')
          setTimeout(() => {
            window.location.href='subscription-plans'
          }, 2000)
        }
        
      }
    })
 
  },
  onCancel: function(data) {
    alert('You have cancelled your paypal payment transtaction :('); // when user cancels the transtaction
  }
 
 }).render('#paypal-button-container2'); // Renders the PayPal button