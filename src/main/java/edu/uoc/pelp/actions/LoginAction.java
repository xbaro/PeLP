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

import com.opensymphony.xwork2.ActionSupport;
import edu.uoc.pelp.bussines.UOC.UOCPelpBussines;
import edu.uoc.pelp.bussines.UOC.vo.UOCClassroom;
import edu.uoc.pelp.bussines.UOC.vo.UOCSubject;
import edu.uoc.pelp.bussines.exception.AuthorizationException;
import edu.uoc.pelp.bussines.exception.InvalidEngineException;
import edu.uoc.pelp.bussines.vo.UserInformation;
import edu.uoc.pelp.exception.ExecPelpException;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.apache.struts2.ServletActionContext;
import org.apache.struts2.convention.annotation.Namespace;
import org.apache.struts2.convention.annotation.Result;
import org.apache.struts2.convention.annotation.ResultPath;
import org.apache.struts2.convention.annotation.Results;
import org.apache.struts2.interceptor.SessionAware;
import org.springframework.web.context.WebApplicationContext;
import org.springframework.web.context.support.WebApplicationContextUtils;

/**
 * Action class for administration page
 * @author Xavier Baró
 */
@Namespace("/")
@ResultPath(value = "/")
@Results({
    @Result(name = "success", location = "WEB-INF/jsp/login.jsp"),
    @Result(name = "login", location = "login.html", type="redirect")
})
public class LoginAction extends ActionSupport implements SessionAware {
 
    protected Map<String, Object> session = null;
 
    private static final long serialVersionUID = 1L;

    private String btnLogin;
    private String btnLogout;
    private UOCPelpBussines bussines;
    private UserInformation person;
    private String userFullName;
    private String userPhoto;
    private UOCSubject[] listSubjects;
    private UOCClassroom[] listClassroms;
    
    @Override
    public String execute() {
        
        WebApplicationContext context =
			WebApplicationContextUtils.getRequiredWebApplicationContext(
                                    ServletActionContext.getServletContext()
                        );
        bussines = (UOCPelpBussines)context.getBean("pelpBussines");
        
        if(btnLogin!=null) {
            person=null;
        }
        
        if(btnLogout!=null) {
            person=null;
        }
        
        if(bussines!=null && !bussines.isUserAuthenticated()) {
            session.put("authUOC", "request");
            return "login";
        }
       
        if(bussines!=null) {
            try {
                person=bussines.getUserInformation();  
                if(person!=null) {
                    userFullName=person.getUserFullName();
                    userPhoto=person.getUserPhoto();
                }
                listSubjects=bussines.getUserSubjects();
                //private UOCClassroom[] listClassroms;
                
            } catch (AuthorizationException ex) {
                Logger.getLogger(LoginAction.class.getName()).log(Level.SEVERE, null, ex);
            } catch (ExecPelpException ex) {
                Logger.getLogger(LoginAction.class.getName()).log(Level.SEVERE, null, ex);
            } catch (InvalidEngineException ex) {
                Logger.getLogger(LoginAction.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
        return SUCCESS;
    } 

    public String getBtnLogin() {
        return btnLogin;
    }

    public void setBtnLogin(String btnLogin) {
        this.btnLogin = btnLogin;
    }

    public String getBtnLogout() {
        return btnLogout;
    }

    public void setBtnLogout(String btnLogout) {
        this.btnLogout = btnLogout;
    }

    public UOCPelpBussines getBussines() {
        return bussines;
    }

    public void setBussines(UOCPelpBussines bussines) {
        this.bussines = bussines;
    }

    public UserInformation getPerson() {
        return person;
    }

    public void setPerson(UserInformation person) {
        this.person = person;
    }
    
    @Override
    public void setSession(Map<String, Object> session) {
        this.session = session;
 
    }

    public String getUserFullName() {
        return userFullName;
    }

    public void setUserFullName(String userFullName) {
        this.userFullName = userFullName;
    }

    public String getUserPhoto() {
        return userPhoto;
    }

    public void setUserPhoto(String userPhoto) {
        this.userPhoto = userPhoto;
    }

    
}