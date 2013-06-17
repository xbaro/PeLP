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
import edu.uoc.pelp.bussines.vo.UserInformation;
import edu.uoc.pelp.engine.campus.UOC.CampusConnection;
import edu.uoc.pelp.model.vo.UOC.Semester;
import edu.uoc.pelp.test.tempClasses.LocalCampusConnection;


/**
 * 
 * Class for semester management
 * 
 * @author jmangas
 * 
 */
@ParentPackage(value = "default")
@InterceptorRefs(value = { @InterceptorRef(value = "langInterceptor"), @InterceptorRef(value = "defaultStack") })

@Namespace("/")
@ResultPath(value = "/")
@Results({
		@Result(name = "success", location = "WEB-INF/jsp/adminSemester.jsp"),
		@Result(name="rsuccess", type="redirectAction", params = {"actionName" , "admin"}),
})

public class AdminAction extends ActionSupport {

	private static final long serialVersionUID = 3165462908903079864L;
	
	private UOCPelpBussines bUOC;
	
	public Semester[] semesterList;
	public String semester;
	public String start;
	public String end;
	
	private String username;
	private String imageURL;
	private String fullName;
	
	public boolean isAdmin = false;
	
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
    	
        	isAdmin = bUOC.isAdministrator();
        	if( isAdmin ){
        		
        		// FiXME obtener el listado de semestres activos
        		semesterList = new Semester[2];
        		Semester sem = new Semester("20121");
        		semesterList[0] = sem;
        		sem = new Semester("20122");
        		semesterList[1] = sem;
        	}
    	
    	
    	} else {
    		imageURL = null;
    		fullName = null;
    	}
    	

    	
		return SUCCESS;
	}
	
	public String add()  throws Exception{
		
    	isAdmin = bUOC.isAdministrator();
    	if( isAdmin ){
			SimpleDateFormat simpleDateFormat = new SimpleDateFormat("dd/mm/yy");
			Date startDate = simpleDateFormat.parse(start);
			Date endDate = simpleDateFormat.parse(end);
			bUOC.addSemester(semester, startDate, endDate);
    	}
		return SUCCESS;
	}
	
	public String remove()  throws Exception{
    	isAdmin = bUOC.isAdministrator();
    	if( isAdmin ){	
    		bUOC.removeSemester(semester);
    	}
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

	public boolean isAdmin() {
		return isAdmin;
	}

	public void setAdmin(boolean isAdmin) {
		this.isAdmin = isAdmin;
	}

	
}
