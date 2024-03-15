$(document).ready(function () {
  // 각 Save 버튼에 클릭 이벤트 추가
  $('.save-btn').click(function () {
    var field = $(this).data('field');
    var value = $('#' + field).val();
    saveData(field, value);
  });

  // Save 버튼 클릭 시 데이터 저장
  function saveData(field, value) {
    $.ajax({
      type: 'POST',
      url: '/save_data',
      data: JSON.stringify({ field: field, value: value }),
      contentType: 'application/json',
      success: function (response) {
        console.log('Data saved successfully!');
        // 저장된 값들을 다시 불러와서 표시
        getSavedValues();
      },
      error: function (xhr, status, error) {
        console.error('Error saving data:', error);
      },
    });
  }

  // 저장된 값들을 가져와서 HTML에 표시
  function getSavedValues() {
    $.ajax({
      type: 'GET',
      url: '/get_data',
      success: function (response) {
        $('#savedValues').html(response);
      },
      error: function (xhr, status, error) {
        console.error('Error getting saved values:', error);
      },
    });
  }

  // 페이지 로드 시 저장된 값들을 가져와서 표시
  getSavedValues();
});
