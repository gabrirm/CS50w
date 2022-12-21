document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  document.querySelector("#compose-form").addEventListener('submit', send_email);

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#emails-details-view').style.display = 'none';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function view_email(id){
  fetch(`/emails/${id}`)
  .then(response => response.json())
  .then(email => {
  // Print email
    console.log(email);
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'none';
    document.querySelector('#emails-details-view').style.display = 'block';
    document.querySelector('#emails-details-view').innerHTML = `
    <ul class="list-group">
      <li class="list-group-item"><strong>From: </strong>${email.sender}</li>
      <li class="list-group-item"><strong>To: </strong>${email.recipients}</li>
      <li class="list-group-item"><strong>Subject: </strong>${email.subject}</li>
      <li class="list-group-item"><strong>Timestamp: </strong>${email.timestamp}</li>
      <li class="list-group-item"><button id='reply_btn' class='btn btn-primary'>Reply</button></li>
    </ul>
    <hr>
    <p>${email.body}</p>

  `;
    // change read to true
    if (email.read != true) {
      fetch(`/emails/${email.id}`, {
        method: 'PUT',
        body: JSON.stringify({
          read: true
        })
      })
    }
    const btn_arch = document.createElement("button");
    btn_arch.innerHTML = email.archived ? 'Unarchive': 'Archive';
    btn_arch.className = email.archived ? 'btn btn-danger': 'btn btn-success';
    btn_arch.addEventListener('click', function() {
      fetch(`/emails/${email.id}`, {
        method: 'PUT',
        body: JSON.stringify({
            archived: !email.archived
        })
      })
      .then(() => { load_mailbox('archive')})
    })
    document.querySelector("#emails-details-view").append(btn_arch);
    const reply_btn = document.querySelector("#reply_btn");
    reply_btn.className = "btn btn-info px-2";
    reply_btn.addEventListener('click', function() {
      compose_email();
      let subject = email.subject
      if (subject.split(" ", 1)[0] != "Re:") {
        subject = "Re: " + email.subject;
      }
      document.querySelector('#compose-recipients').value = email.sender;
      document.querySelector('#compose-subject').value = subject;
      document.querySelector('#compose-body').value = `On ${email.timestamp} wrote: ${email.body}`;
    })

  });
}

  // ... do something else with email ...


function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#emails-details-view').style.display = 'none';

  // Show the mailbox name
  
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
  
  // get the emeails
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    
    //loop through each emails and create div
    emails.forEach(singleEmail => {
      console.log(singleEmail);
      //creaate div
      const newEmail = document.createElement("div");
      newEmail.className = "list-group-item";
      newEmail.innerHTML = `
      <h6>Sender: ${singleEmail.sender}</h6>
      <h5>Subject: ${singleEmail.subject}</h5>
      <p>${singleEmail.body}
      <hr>
      `;
      // change background color
      newEmail.className = singleEmail.read ? 'read': 'unread';
      document.querySelector("#emails-view").append(newEmail);
      newEmail.addEventListener('click', function () {
        view_email(singleEmail.id);
      });
    });
});
}

function send_email(event) {
  //store info
  event.preventDefault();
  const recipients = document.querySelector("#compose-recipients").value;
  const subject = document.querySelector("#compose-subject").value;
  const body = document.querySelector("#compose-body").value;
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: recipients,
        subject: subject,
        body: body
    })
  })
  .then(response => response.json())
  .then(result => {
      // Print result
      console.log(result);
      load_mailbox('sent');
  });
  

};

