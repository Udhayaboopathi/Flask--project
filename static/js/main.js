$(document).ready(function () {
  $("#myForm").submit(function (e) {
    e.preventDefault();

    var name = $("#name").val();
    var age = $("#age").val();
    var email = $("#email").val();
    var message = $("#message").val();

    var jsonData = {
      name: name,
      age: age,
      email: email,
      message: message,
    };

    console.log(jsonData);

    $.ajax({
      url: "/submit_form",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify(jsonData),
      success: function (response) {
        alert(response.message);
        $("#myForm")[0].reset();
      },
      error: function (xhr, status, error) {
        console.log(error);
      },
    });
  });
});

$(document).ready(function () {
  $.ajax({
    url: "/data",
    type: "GET",
    success: function (response) {
      console.log(response);
      $("#users-table").DataTable({
        data: response,
        columns: [
          { data: "id" },
          { data: "name" },
          { data: "age" },
          { data: "email" },
          { data: "message" },
        ],
      });
    },
  });
});

$(document).ready(function () {
  $("#searchButton").click(function () {
    var userId = $("#userIdInput").val();

    $.ajax({
      url: "/user/" + userId,
      type: "GET",
      success: function (response) {
        if (response.error) {
          console.log(response.error);
        } else {
          var userData = response;
          console.log(userData);
          $("#userDataContainer").append(
            "<tr><td>" +
              userData.id +
              "</td><td>" +
              userData.name +
              "</td><td>" +
              userData.age +
              "</td><td>" +
              userData.email +
              "</td><td>" +
              userData.message +
              "</td></tr>"
          );
          console.log(userData.id);
        }
      },
      error: function (xhr, status, error) {
        console.error(error);
      },
    });
  });
});

$(document).ready(function () {
  $("#registerForm").submit(function (e) {
    e.preventDefault();

    var username = $("#username").val();
    var password = $("#password").val();

    var jsonData = {
      username: username,
      password: password,
    };

    console.log(jsonData);

    $.ajax({
      url: "/registers_submit",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify(jsonData),
      success: function (response) {
        alert(response.message);
        $("#registerForm")[0].reset();
      },
      error: function (xhr, status, error) {
        console.log(error);
      },
    });
  });
});

$(document).ready(function () {
  $("#loginForm").submit(function (e) {
    e.preventDefault();
    var username = $("#username").val();
    var password = $("#password").val();
    var jsonData = {
      username: username,
      password: password,
    };

    $.ajax({
      url: "/login1",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify(jsonData),
      success: function (response) {
        alert(response.message);
        $("#loginForm")[0].reset();
      },
      error: function (xhr, status, error) {
        console.log(error);
      },
    });
  });
});
