$(document).ready(function () {
    // this function will call when the member dialog opened
    setMemberData();


    const adminDeleteMemberBtns = $(".admin-delete-member-list-btn");
    adminDeleteMemberBtns.on("click", (event) => {
        adminDeleteMember(event.currentTarget);
    });


    const adminFilterMembersBtn = $("#admin-members-filter-btn");
    adminFilterMembersBtn.on("click", (event) => {
        membersFilterListView();
    });


    // this btns to fetch details for member in member list view
    const memberDetailsBtns = $('.member-details-btn');
    memberDetailsBtns.on('click', (event) => {
      const viewUserModal = $("#viewUserModal");
      const clickedBtn = $(event.currentTarget);
      const memberID = parseInt(clickedBtn.data('memberId'));
      sessionStorage.setItem("clickedMember", memberID);  // save the clicked member
      viewUserModal.modal('show');
    });
})
