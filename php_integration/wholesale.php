<?php

if (!defined('BASEPATH'))

    exit('No direct script access allowed');

class Wholesale extends MY_Controller

{

    function __construct()

    {

        parent::__construct();

        $this->load->model('Cms_model', '', TRUE);

        $this->load->model('Banner_model', '', TRUE);  

		$this->load->model('Wholesale_model', '', TRUE);		

       
		
    }    

    public function index($url='wholesale')

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

		$data_msg['states_data'] 			=	$states_data         = $this->Wholesale_model->get_states();

			

		if( isset($_POST['action']) && $_POST['action'] == 'Save_Data' ){	

		    

			$error_msg 			  = '';

		    $post_data            = $_POST['data'];

				

			

			$this->load->library('form_validation');

			$this->form_validation->set_rules('data[business_name]', 'Business Name', 'trim|required|xss_clean');

			$this->form_validation->set_rules('data[fname]', 'First Name', 'trim|required|xss_clean');

			$this->form_validation->set_rules('data[lname]', 'Last Name', 'trim|required|xss_clean');

			$this->form_validation->set_rules('data[address]', 'Address', 'trim|required|xss_clean');

			$this->form_validation->set_rules('data[city]', 'City', 'trim|required|xss_clean');

			$this->form_validation->set_rules('data[state]', 'State', 'trim|required|xss_clean');

			$this->form_validation->set_rules('data[zip_code]', 'Zip Code', 'trim|required|xss_clean');

			$this->form_validation->set_rules('data[website]', 'Website', 'trim|required|xss_clean');							

			$this->form_validation->set_rules('data[email]', 'Email', 'trim|required|valid_email|xss_clean');	

			$this->form_validation->set_rules('data[telephone]', 'Telephone', 'trim|required|xss_clean');	

						

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

				'message' 			=> $this->load->view('wholesale_partial/wholesale_form', $data_msg, true)

				));		

				exit;	

				

			}

			else{	

					

					$post_data['create_date']   = date('Y-m-d H:i:s');

					$post_data['status']        = '0';

					$this->Wholesale_model->add($post_data);

					$apireturn = $this->apis($post_data);

					$data_msg['data']    = '';					

					echo json_encode(

					array(

					'status'  			=> 'success', 

					'message' 			=> $this->load->view('wholesale_partial/wholesale_form',$data_msg,true),					

					'success_message' 	=> 'Thank you for your interest. We will be glad to assist you.'

					));		

					exit;					

			}			

            

		}		

		$this->view('wholesale', $data_msg); 

		

    }
	
	// API to data send (shop.zomoamerica.com) erpnext Open
    protected function apis($postdata){
		
		if (! function_exists ( 'curl_version' )) {
			return array("error"=>"Enable cURL in PHP");
		}
		
		if($postdata){
			$url = 'https://shop.zomoamerica.com/api/method/zomoamerica.api.create_lead';
			
			$usstates_territory = array("Maine"=>"EAST COAST","New Hampshire"=>"EAST COAST","Vermont"=>"EAST COAST","Massachusetts"=>"EAST COAST","Rhode Island"=>"EAST COAST","Connecticut"=>"EAST COAST","New York"=>"EAST COAST","New Jersey"=>"EAST COAST","Pennsylvania"=>"EAST COAST","Delaware"=>"EAST COAST","Maryland"=>"EAST COAST","DC"=>"EAST COAST","Virginia "=>"EAST COAST","West Virginia"=>"EAST COAST","Ohio"=>"EAST COAST","Michigan"=>"EAST COAST","North Carolina"=>"EAST COAST","South Carolina"=>"EAST COAST","Wisconsin"=>"EAST COAST","Illinois"=>"EAST COAST","Indiana"=>"EAST COAST","Kentucky"=>"EAST COAST","Tennesse"=>"EAST COAST","Mississippi"=>"EAST COAST","Alabama"=>"EAST COAST","Georgia"=>"EAST COAST","Florida"=>"EAST COAST","Minnesota"=>"CENTRAL  ZONE","Iowa"=>"CENTRAL  ZONE","Missouri"=>"CENTRAL  ZONE","Arkansas"=>"CENTRAL  ZONE","Louisiana"=>"CENTRAL  ZONE","North Dakota"=>"CENTRAL  ZONE","South Dakota"=>"CENTRAL  ZONE","Nebraska"=>"CENTRAL  ZONE","Kansas"=>"CENTRAL  ZONE","Oklahama"=>"CENTRAL  ZONE","Texas"=>"CENTRAL  ZONE","Montana"=>"CENTRAL  ZONE","Wyoming"=>"CENTRAL  ZONE","Colorado"=>"CENTRAL  ZONE","New Mexico"=>"CENTRAL  ZONE","Washington"=>"WESTCOAST","Idaho"=>"WESTCOAST","Utah"=>"WESTCOAST","Arizona"=>"WESTCOAST","Oregon"=>"WESTCOAST","Nevada"=>"WESTCOAST","California"=>"WESTCOAST","Alaska"=>"WESTCOAST");
			
			$usstates = array("Alabama"=>"AL","Alaska"=>"AK","Arizona"=>"AZ","Arkansas"=>"AR","California"=>"CA","Colorado"=>"CO","Connecticut"=>"CT","Delaware"=>"DE","Florida"=>"FL","Georgia"=>"GA","Hawaii"=>"HI","Idaho"=>"ID","Illinois"=>"IL","Indiana"=>"IN","Iowa"=>"IA","Kansas"=>"KS","Kentucky"=>"KY","Louisiana"=>"LA","Maine"=>"ME","Maryland"=>"MD","Massachusetts"=>"MA","Michigan"=>"MI","Minnesota"=>"MN","Mississippi"=>"MS","Missouri"=>"MO","Montana"=>"MT","Nebraska"=>"NE","Nevada"=>"NV","New Hampshire"=>"NH","New Jersey"=>"NJ","New Mexico"=>"NM","New York"=>"NY","North Carolina"=>"NC","North Dakota"=>"ND","Ohio"=>"OH","Oklahoma"=>"OK","Oregon"=>"OR","Pennsylvania"=>"PA","Rhode Island"=>"RI","South Carolina"=>"SC","South Dakota"=>"SD","Tennessee"=>"TN","Texas"=>"TX","Utah"=>"UT","Vermont"=>"VT","Virginia"=>"VA","Washington"=>"WA","West Virginia"=>"WV","Wisconsin"=>"WI","Wyoming"=>"WY"); 
		
			
			$state = $postdata['state'];
			
			$territory = 'United States';
			if(array_key_exists($state,$usstates_territory)){
				$territory = $usstates_territory[$state];
			}
			
			if(array_key_exists($state,$usstates)){
				$state = $usstates[$state];
			}
			
			
			
			
			$apiData = array();
			
			$apiData= array('business_name'=>$postdata['business_name'],'first_name'=>$postdata['fname'],'last_name'=>$postdata['lname'],'address'=>$postdata['address'],'city'=>$postdata['city'],'state'=>$state,'zipcode'=>$postdata['zip_code'],'website'=>$postdata['website'], 'email_address'=>$postdata['email'], 'telephone_number'=>$postdata['telephone'], 'territory'=>$territory); 
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
