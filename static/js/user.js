const BIZ_NAME_COL = 0;
const BIZ_ADDRESS_COL = 1;
const REVIEW_DATE_COL = 2;
const STATUS_COL = 3;

$(document).ready(function () {
  $("#user_reviews_table").DataTable({
    pageLength: 50,
    order: [[REVIEW_DATE_COL, "desc"]],
    autoWidth: false,
  });
});
