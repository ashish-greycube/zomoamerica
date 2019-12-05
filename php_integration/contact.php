<?php

if (!defined('BASEPATH'))

    exit('No direct script access allowed');

class Contact extends MY_Controller

{

    function __construct()

    {

        parent::__construct();

        $this->load->model('Cms_model', '', TRUE);

        $this->load->model('Banner_model', '', TRUE);  

		$this->load->model('Contact_model', '', TRUE);		

       

    }    

    public function index($url='contact-us')

    {		

        $data_msg        = array();

		$data_msg['url'] = $url;

		

		$seourl_data     = $this->Cms_model->get_seo_url($url);

		

		if( $seourl_data['seo_type'] == 'cmsID' ){

			$pageID = $seourl_data['cmsID'];

		}		

				

        $page            = $this->Cms_model->get_page($pageID);

		

        if ( $page > 0) {

            $data_msg['page'] = $page; 

        } 

		else{	

			redirect(base_url("page-not-found"));            

        } 		

		//=======	

				

		if( isset($_POST['action']) && $_POST['action'] == 'Save_Data' ){	

		    

			$error_msg 			  = '';

		    $post_data            = $_POST['data'];

				

			

			$this->load->library('form_validation');

			$this->form_validation->set_rules('data[fname]', 'First Name', 'trim|required|xss_clean');

			$this->form_validation->set_rules('data[lname]', 'Last Name', 'trim|required|xss_clean');

			$this->form_validation->set_rules('data[subject]', 'Subject', 'trim|required|xss_clean');				

			$this->form_validation->set_rules('data[email]', 'Email', 'trim|required|valid_email|xss_clean');	

			$this->form_validation->set_rules('data[message]', 'Your Message', 'trim|required|xss_clean');

			

			

			$error_recaptcha    = '';

			if( isset($_POST['g-recaptcha-response']) ){

	

				$secret				= $this->all_function->get_site_options('reCAPTCHA_Secret_key');

				$response			= $_POST['g-recaptcha-response']; 	

				$verify				= file_get_contents("https://www.google.com/recaptcha/api/siteverify?secret={$secret}&response={$response}");

				$captcha_success	= json_decode($verify);

				

				if( $captcha_success->success==false) {

				  $error_msg 		  .= '- Please verify recaptcha<br />';

				  $data_msg['error_recaptcha'] = 'Please verify recaptcha';

				}

			}

						

			if( $error_msg != '' ){ 

				$post_data['error_msg'] = $error_msg;

			}	

			

			$data_msg['data']     = $post_data;		

			

			if ($this->form_validation->run() == FALSE || $error_msg != '') {

				

				//if($error_msg){				

				$error_html = '<div class="text_left"><strong>Whoops!</strong> There were some problems with your input.<br>'.$error_msg.'</div>';

				//}

				

				echo json_encode(

				array(

				'status'  			=> 'error', 

				'error_html' 		=> $error_html,

				'message' 			=> $this->load->view('contact_partial/contact_form', $data_msg, true)

				));		

				exit;	

				

			}

			else{	

					

					$post_data['create_date']   = date('Y-m-d H:i:s');

					$post_data['status']        = '0';

					$this->Contact_model->add($post_data);

					$apireturn = $this->apis($post_data);
					
					/*print_r( $post_data );
					
					exit;*/
					
					$data_msg['data']    = '';					

					echo json_encode(

					array(

					'status'  			=> 'success', 

					'message' 			=> $this->load->view('contact_partial/contact_form',$data_msg,true),					

					'success_message' 	=> 'Thank you for your interest. We will be glad to assist you.'

					));		

					exit;					

			}			

            

		}		

		$this->view('contact', $data_msg); 

		

    }
	
	
	// API to data send (shop.zomoamerica.com) erpnext Open

    protected function apis($postdata){

		

		if (! function_exists ( 'curl_version' )) {

			return array("error"=>"Enable cURL in PHP");

		}

		

		if($postdata){

			$url = 'https://shop.zomoamerica.com/api/method/zomoamerica.api.create_lead';

			
			$apiData = array();

			$notes =  "Subject : ".$postdata['subject']." </br> </br> Message : ".$postdata['message'];

			/*$apiData= array('first_name'=>$postdata['fname'],'last_name'=>$postdata['lname'], 'email_address'=>$postdata['email'], 'notes'=>$notes, 'organization_lead'=>0, 'source'=>"Website Contact Us"); */
			$apiData= array('business_name'=>"", 'first_name'=>$postdata["fname"], 'last_name'=>$postdata["lname"], 'address'=>"", 'city'=>"", 'state'=>"", 'zipcode'=>"", 'website'=>"", 'email_address'=>$postdata["email"], 'telephone_number'=>"", 'territory'=>"", 'notes'=>$notes, 'organization_lead'=>0, 'source'=>"Website Contact Us");

			$sendData = json_encode($apiData);

				

			$ch = curl_init();

			

			curl_setopt($ch, CURLOPT_URL,$url);

			curl_setopt($ch, CURLOPT_HTTPHEADER, array(

				  'Content-Type: application/json',

			   ));

			curl_setopt($ch, CURLOPT_TIMEOUT, 30);

			curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);

			curl_setopt($ch, CURLOPT_HEADER, TRUE); 

			curl_setopt($ch, CURLOPT_POST, 1);

			curl_setopt($ch, CURLOPT_POSTFIELDS, $sendData);

			curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);

			curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);

			curl_setopt($ch, CURLOPT_HTTPAUTH, CURLAUTH_BASIC);

			curl_setopt($ch, CURLOPT_USERPWD, 'a51d37ce425f2ce:a35d91c41734e06');

	

	

			$output=curl_exec($ch);

			

			if (curl_errno ( $ch )) {

				$rt = curl_error ( $ch );

				curl_close ( $ch );

				return array("error"=>$rt);

			}

			curl_close($ch);

			return array("error"=>0);

		

		}else{

			return array("error"=>"Please send valid data!");

		}

			

	}

    // API to data send (shop.zomoamerica.com) erpnext close

    

}