package edu.uoc.pelp.actions;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;

import org.apache.struts2.ServletActionContext;
import org.apache.struts2.convention.annotation.InterceptorRef;
import org.apache.struts2.convention.annotation.InterceptorRefs;
import org.apache.struts2.convention.annotation.Namespace;
import org.apache.struts2.convention.annotation.ParentPackage;
import org.apache.struts2.convention.annotation.Result;
import org.apache.struts2.convention.annotation.ResultPath;
import org.apache.struts2.convention.annotation.Results;
import org.springframework.web.context.WebApplicationContext;
import org.springframework.web.context.support.WebApplicationContextUtils;

import com.opensymphony.xwork2.ActionContext;
import com.opensymphony.xwork2.ActionSupport;

import edu.uoc.pelp.bussines.UOC.UOCPelpBussines;
import edu.uoc.pelp.bussines.UOC.vo.UOCSubject;
import edu.uoc.pelp.bussines.vo.MultilingualText;
import edu.uoc.pelp.bussines.vo.MultilingualTextArray;
import edu.uoc.pelp.bussines.vo.Subject;
import edu.uoc.pelp.bussines.vo.Test;
import edu.uoc.pelp.bussines.vo.UserInformation;
import edu.uoc.pelp.engine.activity.Activity;
import edu.uoc.pelp.engine.activity.ActivityID;
import edu.uoc.pelp.engine.activity.ActivityTest;
import edu.uoc.pelp.engine.activity.DAOActivityManager;
import edu.uoc.pelp.engine.activity.TestID;
import edu.uoc.pelp.engine.campus.UOC.CampusConnection;
import edu.uoc.pelp.engine.campus.UOC.Semester;
import edu.uoc.pelp.engine.campus.UOC.SubjectID;
import edu.uoc.pelp.exception.AuthPelpException;
import edu.uoc.pelp.test.tempClasses.LocalCampusConnection;


/**
 * 
 * Class for subjects management
 * 
 * @author jmangas
 * 
 */
@ParentPackage(value = "default")
@InterceptorRefs(value = { @InterceptorRef(value = "langInterceptor"), @InterceptorRef(value = "defaultStack") })

@Namespace("/")
@ResultPath(value = "/")
@Results({
		@Result(name = "success", location = "WEB-INF/jsp/adminActivities.jsp"),
		@Result(name="rsuccess", type="redirectAction", params = {"actionName" , "admin-activities"}),
})

public class AdminActivitiesAction extends ActionSupport {

	private static final long serialVersionUID = 3165462908903079864L;
	
	private UOCPelpBussines bUOC;
	
	private UOCSubject[] subjectsList;
	private edu.uoc.pelp.bussines.vo.Activity[] activitiesList;	
	private ActivityTest[] testList;
	
	public Semester[] semesterList;
	public String semester;
	public String subject;
	public String subjectID;
	private edu.uoc.pelp.bussines.vo.Activity activity;
	public ActivityTest activityTest;
	public Integer activityIndex;
	public String start;
	public String end;
	public Integer maxDelivers;
	public String progLangCode;
	
	public String activityDescriptionCat;
	public String activityDescriptionEs;
	
	private String username;
	private String imageURL;
	private String fullName;
	
	// TODO cambiar a false al finalizar el desarrollo
	public boolean isTeacher = true;
	
	@Override
	public String execute() throws Exception {

		//UOC API
		HttpServletRequest request = ServletActionContext.getRequest();
    	
    	String token = (String) request.getSession().getAttribute("access_token");
    	if( token != null) {
            WebApplicationContext context =
        			WebApplicationContextUtils.getRequiredWebApplicationContext(
                                            ServletActionContext.getServletContext()
                                );
            CampusConnection campusConnection = (CampusConnection) context.getBean("lcctj");
            campusConnection.setCampusSession(token);
            bUOC.setCampusConnection(campusConnection);
    	}
    	
    	
    	UserInformation userInfo = bUOC.getUserInformation();

    	if(userInfo!= null){
    		String lang = userInfo.getLanguage();
    		System.out.println("IDIOMA USUARIO: "+lang);
    		Map session = ActionContext.getContext().getSession();	
    		if(lang.equals("ca")){
    			session.put("WW_TRANS_I18N_LOCALE",new java.util.Locale("ca"));
    			Locale locale = new Locale("ca", "ES");
    			session.put("org.apache.tiles.LOCALE", locale);
    		}else if(lang.equals("es")){
    			session.put("WW_TRANS_I18N_LOCALE",new java.util.Locale("es"));
    			Locale locale = new Locale("es", "ES");
    			session.put("org.apache.tiles.LOCALE", locale);
    		}else if(lang.equals("en")){
    			session.put("WW_TRANS_I18N_LOCALE",new java.util.Locale("en"));
    			Locale locale = new Locale("en", "UK");
    			session.put("org.apache.tiles.LOCALE", locale);
    		}

    		imageURL = userInfo.getUserPhoto();
    		if(imageURL== null)imageURL = "img/user.png";
    		fullName = userInfo.getUserFullName();

    		// FIXME obtener el listado de subjects del usuario
    		//subjectsList = bUOC.getUserSubjects();  
    		subjectsList = new UOCSubject[2];
    		UOCSubject sub = new UOCSubject("20122", "05.554");
    		sub.setDescription("Introduccion Java"); 
    		subjectsList[0] = sub;   
    		sub = new UOCSubject("20122", "05.556");
    		sub.setDescription("Introduccion Java 2");
    		subjectsList[1] = sub;

    		
    		if( subjectID == null && subjectsList != null && subjectsList.length > 0 ){
	    		subject = subjectsList[0].getSubjectCode();
	    		subjectID = subjectsList[0].getSubjectID();
	    		semester = subjectsList[0].getSemesterCode();
    		} else {
    			if(subjectsList != null  &&  subjectsList.length > 0) {
	    			for (UOCSubject subjectIter : subjectsList) {
						if( subjectIter.getSubjectID().equalsIgnoreCase(subjectID) ){
							subject = subjectIter.getSubjectCode();
							semester = subjectIter.getSemesterCode();
						}
					}
    			}
    		}
    		
    		// FIXME esta validacion tarda mucho tiempo, es necesaria?
    		//isTeacher = bUOC.isTeacher(new UOCSubject(semester, subject));
    		if( !isTeacher ) {
    			throw new AuthPelpException("No valid permisions to edit activities");
    		}
    		
    		
    		if(subjectsList != null &&  subjectsList.length > 0 && subject != null ){

    			// FIXME
    			// obtener listado de actividades
    			//activitiesList = bUOC.getSubjectActivities(semester, subject);    			
    			activitiesList = new edu.uoc.pelp.bussines.vo.Activity[2];
    			edu.uoc.pelp.bussines.vo.Activity activityDummy = new edu.uoc.pelp.bussines.vo.Activity(new Subject(subjectID), 1);
    			activityDummy.setDescription(subjectID + " actividad 1");
    			activitiesList[0] = activityDummy;
    			activityDummy = new edu.uoc.pelp.bussines.vo.Activity(new Subject(subjectID), 2);
    			activityDummy.setIndex(2);
    			activityDummy.setDescription(subjectID + " actividad 2");
    			activitiesList[1] = activityDummy;
    			
    			
        		if( activityIndex == null && activitiesList != null){
        			activityIndex = activitiesList[0].getIndex();        			
        		}
        		
        		// FIXME llamar a DAOActivityManager.getActivity(ActivityID activityID) para obtener los datos de la actividad a partir del activityID
        		//activity = new DAOActivityManager().getActivity(activityID);
        		if( activitiesList != null){
        			activity = activitiesList[activityIndex];
        		}
        		
        		// Cargar datos de la actividad seleccionada
        		
        		
        		
    			// FIXME obtener el listado de test de la actividad seleccionada
    			testList = new ActivityTest[2]; 
    			ActivityID actityID =  new ActivityID( new SubjectID(subject, new Semester(semester)), 1);
    			
    			TestID testId  = new TestID(actityID, 1);
    			ActivityTest test = new ActivityTest(testId);    
    			test.setInputStr("input");
    			test.setExpectedOutputStr("ouptput");
    			testList[0] = test;
    			
    			
    			activityTest = testList[0];
    		}
    		
    	
    	
    	} else {
    		imageURL = null;
    		fullName = null;
    	}
    	

    	
		return SUCCESS;
	}
	
	public String addActivity()  throws Exception{
		   	   	
		SimpleDateFormat simpleDateFormat = new SimpleDateFormat("dd/mm/yy");
		Date startDate = simpleDateFormat.parse(start);
		Date endDate = simpleDateFormat.parse(end);
		MultilingualTextArray  activityDescriptions = new MultilingualTextArray(2);
		activityDescriptions.setText(0, new MultilingualText("ca",  activityDescriptionCat ) );
		activityDescriptions.setText(1, new MultilingualText("es",  activityDescriptionEs ) );
		
		edu.uoc.pelp.bussines.vo.Subject subject = new edu.uoc.pelp.bussines.vo.Subject( subjectID );
		// FIXME este metodo da un error al añadir la actividad
		bUOC.addActivity(subject, startDate, endDate, maxDelivers, progLangCode, activityDescriptions);    	
		return SUCCESS;
	}
	
	public String editActivity()  throws Exception{
   	   	
		SimpleDateFormat simpleDateFormat = new SimpleDateFormat("dd/mm/yy");
		Date startDate = simpleDateFormat.parse(start);
		Date endDate = simpleDateFormat.parse(end);
		MultilingualTextArray  activityDescriptions = new MultilingualTextArray(2);
		activityDescriptions.setText(0, new MultilingualText("ca",  activityDescriptionCat ) );
		activityDescriptions.setText(1, new MultilingualText("es",  activityDescriptionEs ) );
		
		edu.uoc.pelp.bussines.vo.Subject subject = new edu.uoc.pelp.bussines.vo.Subject( subjectID );
		// FIXME falta el metodo de editar actividad
		
		return SUCCESS;
	}
	
	public String addTest()  throws Exception{
   	   	
		// FIXME falta el metodo para añadir test
		return SUCCESS;
	}
	
	
	
	public String removeTest()  throws Exception{

    		
    	// FIXME llamar a removeTest
    	
    	
		return SUCCESS;
	}
	

	
	
	
	public String auth() throws Exception {

		HttpServletRequest request = ServletActionContext.getRequest();
		request.getSession().setAttribute("authUOC", "request");

		String toReturn = 'r'+SUCCESS;

		return toReturn;
	}
	
	public String logout() throws Exception {

		HttpServletRequest request = ServletActionContext.getRequest();
    	request.getSession().setAttribute("authUOC", "close");
		LocalCampusConnection _campusConnection = new LocalCampusConnection();
		        // Add the register to the admin database to give administration rights
		        _campusConnection.setProfile("none");
		        
		        bUOC.setCampusConnection(_campusConnection);
		        
		String toReturn = 'r'+SUCCESS;


		return toReturn;
	}

	
	public UOCPelpBussines getbUOC() {
		return bUOC;
	}

	public void setbUOC(UOCPelpBussines bUOC) {
		this.bUOC = bUOC;
	}

	public String getSemester() {
		return semester;
	}

	public void setSemester(String semester) {
		this.semester = semester;
	}



	public String getUsername() {
		return username;
	}

	public void setUsername(String username) {
		this.username = username;
	}

	public String getImageURL() {
		return imageURL;
	}

	public void setImageURL(String imageURL) {
		this.imageURL = imageURL;
	}

	public String getFullName() {
		return fullName;
	}

	public void setFullName(String fullName) {
		this.fullName = fullName;
	}

	public boolean isTeacher() {
		return isTeacher;
	}

	public void setTeacher(boolean isTeacher) {
		this.isTeacher = isTeacher;
	}

	public UOCSubject[] getSubjectsList() {
		return subjectsList;
	}

	public void setSubjectsList(UOCSubject[] subjectsList) {
		this.subjectsList = subjectsList;
	}




	public String getStart() {
		return start;
	}

	public void setStart(String start) {
		this.start = start;
	}

	public String getEnd() {
		return end;
	}

	public void setEnd(String end) {
		this.end = end;
	}



	public String getProgLangCode() {
		return progLangCode;
	}

	public void setProgLangCode(String progLangCode) {
		this.progLangCode = progLangCode;
	}

	public Semester[] getSemesterList() {
		return semesterList;
	}

	public void setSemesterList(Semester[] semesterList) {
		this.semesterList = semesterList;
	}

	public String getSubject() {
		return subject;
	}

	public void setSubject(String subject) {
		this.subject = subject;
	}

	public Integer getMaxDelivers() {
		return maxDelivers;
	}

	public void setMaxDelivers(Integer maxDelivers) {
		this.maxDelivers = maxDelivers;
	}

	public String getActivityDescriptionCat() {
		return activityDescriptionCat;
	}

	public void setActivityDescriptionCat(String activityDescriptionCat) {
		this.activityDescriptionCat = activityDescriptionCat;
	}

	public String getActivityDescriptionEs() {
		return activityDescriptionEs;
	}

	public void setActivityDescriptionEs(String activityDescriptionEs) {
		this.activityDescriptionEs = activityDescriptionEs;
	}

	public static long getSerialversionuid() {
		return serialVersionUID;
	}


	public String getSubjectID() {
		return subjectID;
	}

	public void setSubjectID(String subjectID) {
		this.subjectID = subjectID;
	}



	public edu.uoc.pelp.bussines.vo.Activity[] getActivitiesList() {
		return activitiesList;
	}

	public void setActivitiesList(edu.uoc.pelp.bussines.vo.Activity[] activitiesList) {
		this.activitiesList = activitiesList;
	}

	public void setActivityIndex(Integer activityIndex) {
		this.activityIndex = activityIndex;
	}

	public ActivityTest[] getTestList() {
		return testList;
	}

	public void setTestList(ActivityTest[] testList) {
		this.testList = testList;
	}


	public Integer getActivityIndex() {
		return activityIndex;
	}

	public edu.uoc.pelp.bussines.vo.Activity getActivity() {
		return activity;
	}

	public void setActivity(edu.uoc.pelp.bussines.vo.Activity activity) {
		this.activity = activity;
	}

	public ActivityTest getActivityTest() {
		return activityTest;
	}

	public void setActivityTest(ActivityTest activityTest) {
		this.activityTest = activityTest;
	}





	
}
