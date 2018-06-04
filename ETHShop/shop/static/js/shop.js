async function buy_content() {
  var session_id = $('input[name=session_id]').val();
  var new_receipt_value = $('input[name=new_receipt_value]').val();
  var etherum_address = await getEtherumAddress();
  var receipt = await getReceipt(session_id, new_receipt_value, etherum_address);
  $('input[name=receipt]').val(receipt);
}

$( document ).ready(function() {
    $('.buy_content_form').submit(function() {
        var form = $(this);
        buy_content().then(result => {
          form[0].submit();
        });
        return false;
    })
});
