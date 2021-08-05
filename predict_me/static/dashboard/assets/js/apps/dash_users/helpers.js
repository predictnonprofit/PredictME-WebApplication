function setMemberData() {
  const controller = new AbortController();
  const {
    signal
  } = controller;
  // this function will be only for view modal of the user
  // this when click on the view button to display the modal of the clicked user
  $('#viewUserModal').on('shown.bs.modal', function(e) {
    $('#viewUserModal').modal('handleUpdate'); //to readjust the modal’s position in case a scrollbar appears
    // do something...
    const memberID = parseInt(sessionStorage.getItem('clickedMember'));
    try {
      const memberDetailsRequest = fetchMemberDetails(memberID, signal);
      memberDetailsRequest.then(data => {
        setMemberDetailsInModal(data['member']);
        $("#userLoadSpinner").fadeOut(function() {
          $("#user-modal-body").show();
        });

      }).catch(error => {
        console.error('Error in fetch');
      });
    } catch (e) {
      // console.error(e);
      console.error('Error when fetch member details!!');
    }
  });

  // this to hide and reset any variable data of the api to default, to prevent any save to previous user when click on new one
  $('#viewUserModal').on('hidden.bs.modal', function(e) {
    $('#viewUserModal').modal('handleUpdate'); //to readjust the modal’s position in case a scrollbar appears
    // do something...
    console.log("close the modal and reset the data");
    // check if the connection not aborted
    // if (!signal.aborted){
    //   controller.abort(); // to abort the request
    //   console.log(signal.aborted);
    // }
    $("#user-modal-body").fadeOut(function() {
      $("#userLoadSpinner").show();
      sessionStorage.clear(); // delete the clicked member id
      const dMemberEditLink = $('#dMemberEditLink');
      dMemberEditLink.attr('href', "#");
      dMemberEditLink.addClass("disabled-link not-allowed-cursor");

    });
  });
}


// this function will fire when click delete member from admin member list view
function adminDeleteMember(btnElement) {
  Swal.fire({
    title: 'Are you sure?',
    text: "Do you want to delete this user?",
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#3085d6',
    cancelButtonColor: '#d33',
    confirmButtonText: 'Yes, delete it!',
    allowOutsideClick: false,
    allowEscapeKey: false,
    allowEnterKey: false,
  }).then((result) => {
    if (result.isConfirmed) {
      const btn = $(btnElement);
      const memberID = btn.data("member-id");
      console.log(memberID);
      Swal.fire(
        'Deleted!',
        'Your file has been deleted.',
        'success'
      );
      location.reload();
    }
  });


}


// this function will fire when admin want to filter the members list view
function membersFilterListView() {
  alert("filter members list view");
}


// this function will fill the member info to member modal
function setMemberDetailsInModal(memberData) {
  // console.info('Set member info in member modal');
  // console.info(memberData);
  // dMemberStarterIcon, dMemberProIcon, dMemberExpertIcon, membership-icon
  const viewMemberModalLabel = $("#viewMemberModalLabel");
  const dMemberName = $("#dMemberName");
  const dMemberEmail = $('#dMemberEmail');
  const dMemberCountry = $('#dMemberCountry');
  const dMemberJobTitle = $("#dMemberJobTitle");
  const dMemberStatus = $("#dMemberStatus");
  const dMemberMembership = $('#dMemberMembership');
  const dMemberRunModelTimes = $('#dMemberRunModelTimes');
  const dMemberTotalSpent = $("#dMemberTotalSpent");
  const dMemberDataUsageProgressbar = $('#dMemberDataUsageProgressbar');
  const dMemberDataUsagePer = $("#dMemberDataUsagePer");
  const dMemberEditLink = $('#dMemberEditLink');
  dMemberEditLink.attr('href', `/dashboard/users/details/${memberData['id']}`);
  dMemberEditLink.removeClass("disabled-link not-allowed-cursor");
  viewMemberModalLabel.text(memberData['full_name']);
  dMemberName.text(memberData['full_name']);
  dMemberEmail.html(`<i class="flaticon2-new-email mr-2 font-size-lg"></i> ${memberData['email']}`);
  dMemberCountry.html(`<i class="flaticon2-placeholder mr-2 font-size-lg"></i> ${memberData['country']}`);
  dMemberStatus.html(`${capitalizeFirstLetter(memberData['status'])}`);
  dMemberJobTitle.html(`<i class="flaticon2-calendar-3 mr-2 font-size-lg"></i> ${memberData['job_title']}`);
  dMemberMembership.text(capitalizeFirstLetter(memberData['membership']));
  dMemberRunModelTimes.text(memberData['run_modal_times']);
  dMemberTotalSpent.text(memberData['total_spent']);
  dMemberDataUsagePer.text(memberData['data_usage_per'] + "%");
  dMemberDataUsageProgressbar.css("width", `${memberData['data_usage_per']}%`);
  // check the user status to set the right label color
  if (memberData['status'] === 'active') {
    dMemberStatus.addClass('label-light-success');
  } else if (memberData['status'] === 'pending') {
    dMemberStatus.addClass('label-light-info');
  } else if ((memberData['status'] === 'cancelled') || (memberData['status'] === 'unverified')) {
    dMemberStatus.addClass('label-light-danger');
  }

  // check the data usage to set the right color
  if ((memberData['data_usage_per'] >= 0) && (memberData['data_usage_per'] <= 50)) {
    dMemberDataUsageProgressbar.addClass('bg-success');
  } else if ((memberData['data_usage_per'] > 50) && (memberData['data_usage_per'] <= 80)) {
    dMemberDataUsageProgressbar.addClass('bg-warning');
  } else if ((memberData['data_usage_per'] > 80) && (memberData['data_usage_per'] <= 100)) {
    dMemberDataUsageProgressbar.addClass('bg-danger');
  }

  // check the membership to enable the correct icon
  if (memberData['membership'] === 'starter') {
    $(".dashboard-member-membership-icon").addClass("d-none");
    $("#dMemberStarterIcon").removeClass('d-none');
  } else if (memberData['membership'] === 'professional') {
    $(".dashboard-member-membership-icon").addClass("d-none");
    $("#dMemberProIcon").removeClass('d-none');
  } else if (memberData['membership'] === 'expert') {
    $(".dashboard-member-membership-icon").addClass("d-none");
    $("#dMemberExpertIcon").removeClass('d-none');
  }
}
