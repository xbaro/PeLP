/*
	Copyright 2011-2012 Fundació per a la Universitat Oberta de Catalunya

	This file is part of PeLP (Programming eLearning Plaform).

    PeLP is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PeLP is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/
package edu.uoc.pelp.actions;

import com.opensymphony.xwork2.ActionContext;
import com.opensymphony.xwork2.ActionSupport;
import edu.uoc.pelp.bussines.UOC.UOCPelpBussines;
import edu.uoc.pelp.bussines.UOC.exception.InvalidSessionException;
import edu.uoc.pelp.bussines.UOC.vo.UOCClassroom;
import edu.uoc.pelp.bussines.UOC.vo.UOCSubject;
import edu.uoc.pelp.bussines.exception.AuthorizationException;
import edu.uoc.pelp.bussines.exception.InvalidEngineException;
import edu.uoc.pelp.bussines.vo.Activity;
import edu.uoc.pelp.bussines.vo.UserInformation;
import edu.uoc.pelp.exception.ExecPelpException;
import org.apache.struts2.ServletActionContext;
import org.apache.struts2.convention.annotation.Action;
import org.apache.struts2.convention.annotation.Actions;
import org.apache.struts2.convention.annotation.Namespace;
import org.apache.struts2.convention.annotation.Result;
import org.apache.struts2.convention.annotation.ResultPath;
import org.springframework.web.context.WebApplicationContext;
import org.springframework.web.context.support.WebApplicationContextUtils;

/**
 * Action class for administration page
 * @author Xavier Baró
 */
@Namespace("/")
@ResultPath(value = "/")
@Result(name = "success", location = "WEB-INF/jsp/admin.jsp")
public class AdminAction extends ActionSupport {

    private static final long serialVersionUID = 1L;

    private UOCPelpBussines bussines;

    private UserInformation userInfo;
    private UOCSubject[] listSubjects;
    private UOCClassroom[] listClassroms;
    private Activity[] listActivity;

    private String s_semester;
    private UOCSubject subject;
    private String s_aula;
    private String s_activ;
    
    private String u_name;

    @Override
    public String execute() {
        WebApplicationContext context =
			WebApplicationContextUtils.getRequiredWebApplicationContext(
                                    ServletActionContext.getServletContext()
                        );
        bussines = (UOCPelpBussines)context.getBean("pelpBussines");
       
        if(bussines!=null) {
            String campusSession=null;
            if(ActionContext.getContext().getParameters().containsKey("s")) {
                Object val = ActionContext.getContext().getParameters().get("s");
                if(val instanceof String[]) {
                    String[] listS=(String[]) val;
                    if(listS.length==1) {
                        campusSession=listS[0];
                    }
                }
            }
            try {
                // Set the session campus
                bussines.setCampusSession(campusSession);
            } catch (InvalidSessionException ex) {
                
            }
            try {
                listSubjects = bussines.getUserSubjects();
            } catch (ExecPelpException ex) {
                listSubjects= null;
            } catch (InvalidEngineException ex) {
                listSubjects= null;
            } catch (AuthorizationException ex) {
                listSubjects= null;
            }
            try {
                //listClassroms = bussines.getUserClassrooms(new UOCSubject(s_semester,s_assign));
                //listActivity = bussines.getSubjectActivities(new UOCSubject(s_semester,s_assign));
                userInfo=bussines.getUserInformation();
            } catch (ExecPelpException ex) {
                userInfo=null;
            } catch (InvalidEngineException ex) {
                userInfo=null;
            }
            u_name=null;
            if(userInfo!=null) {
                u_name=userInfo.getUserFullName();
            }
            
        }
        return SUCCESS;
    }

    public UOCSubject[] getListSubjects() {
        return listSubjects;
    }

    public void setListSubjects(UOCSubject[] listSubjects) {
        this.listSubjects = listSubjects;
    }

    public UOCPelpBussines getBussines() {
        return bussines;
    }

    public void setBussines(UOCPelpBussines bussines) {
        this.bussines = bussines;
    }

    public UOCSubject getSubject() {
        return subject;
    }

    public void setSubject(UOCSubject subject) {
        this.subject = subject;
    }

    public UOCClassroom[] getListClassroms() {
        return listClassroms;
    }

    public void setListClassroms(UOCClassroom[] listClassroms) {
        this.listClassroms = listClassroms;
    }

    public String getS_aula() {
        return s_aula;
    }

    public void setS_aula(String s_aula) {
        this.s_aula = s_aula;
    }

    public String getS_activ() {
        return s_activ;
    }

    public void setS_activ(String s_activ) {
        this.s_activ = s_activ;
    }

    public Activity[] getListActivity() {
        return listActivity;
    }

    public void setListActivity(Activity[] listActivity) {
        this.listActivity = listActivity;
    }

    public String getS_semester() {
        return s_semester;
    }

    public void setS_semester(String s_semester) {
        this.s_semester = s_semester;
    }

    public String getU_name() {
        return u_name;
    }

    public void setU_name(String u_name) {
        this.u_name = u_name;
    }

    public UserInformation getUserInfo() {
        return userInfo;
    }

    public void setUserInfo(UserInformation userInfo) {
        this.userInfo = userInfo;
    }
    
    public String getJSON() {
        return execute();
    }


}
