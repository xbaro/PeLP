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
package edu.uoc.pelp.services;

import edu.uoc.pelp.bussines.UOC.UOCPelpBussines;
import edu.uoc.pelp.bussines.UOC.exception.InvalidSessionException;
import edu.uoc.pelp.bussines.UOC.vo.UOCSubject;
import edu.uoc.pelp.bussines.exception.AuthorizationException;
import edu.uoc.pelp.bussines.exception.InvalidEngineException;
import edu.uoc.pelp.bussines.vo.Activity;
import edu.uoc.pelp.bussines.vo.DeliverDetail;
import edu.uoc.pelp.bussines.vo.Subject;
import edu.uoc.pelp.bussines.vo.UserInformation;
import edu.uoc.pelp.exception.ExecPelpException;
import edu.uoc.pelp.services.vo.SubjectData;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Services implementation class
 * @author Xavier Baró
 */
public class PelpServiceImpl implements PelpService {
    
    private UOCPelpBussines bussines;
    
    /**
     * Default constructor
     */
    public PelpServiceImpl(UOCPelpBussines bussines) {
        super();
        this.bussines=bussines;
    }
    
    @Override
    public UserInformation getUserInformation(String campusSession) {
        UserInformation userInfo=null;
        
        if(bussines!=null) {
            try {
                // Set authentication information
                bussines.setCampusSession(campusSession);
                
                // Get the user information
                userInfo=bussines.getUserInformation();
            } catch (InvalidSessionException ex) {
                Logger.getLogger(PelpServiceImpl.class.getName()).log(Level.SEVERE, null, ex);
            } catch (ExecPelpException ex) {
                Logger.getLogger(PelpServiceImpl.class.getName()).log(Level.SEVERE, null, ex);
            } catch (InvalidEngineException ex) {
                Logger.getLogger(PelpServiceImpl.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
        
        return userInfo;
    }

    @Override
    public SubjectData[] getUserSujects(String campusSession) {
        SubjectData[] ret=null;
        
        if(bussines!=null) {
            try {
                // Set authentication information
                bussines.setCampusSession(campusSession);
                
                // Get subjects for authenticated user
                UOCSubject[] subjects=bussines.getUserSubjects();
                
                // Build output data
                if(subjects!=null) {
                    ret=new SubjectData[subjects.length];
                    for(int i=0;i<subjects.length;i++) {
                        ret[i]=new SubjectData();
                        ret[i].setDescription(subjects[i].getDescription());
                        ret[i].setShortName(subjects[i].getShortName());
                        ret[i].setSemesterCode(subjects[i].getSemesterCode());
                        ret[i].setSubjectCode(subjects[i].getSubjectCode());
                        ret[i].setSubjectID(subjects[i].getSubjectID());
                    }
                }
            } catch (ExecPelpException ex) {
                Logger.getLogger(PelpServiceImpl.class.getName()).log(Level.SEVERE, null, ex);
            } catch (InvalidEngineException ex) {
                Logger.getLogger(PelpServiceImpl.class.getName()).log(Level.SEVERE, null, ex);
            } catch (AuthorizationException ex) {
                Logger.getLogger(PelpServiceImpl.class.getName()).log(Level.SEVERE, null, ex);
            } catch (InvalidSessionException ex) {
                Logger.getLogger(PelpServiceImpl.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
        
        return ret;
    }
    
    @Override
    public Activity[] getSubjectActivities(String campusSession,String subjectID) {
        Activity[] ret=null;
        
        if(bussines!=null && subjectID!=null) {
            try {
                // Set authentication information
                bussines.setCampusSession(campusSession);
                
                // Create the subject object
                UOCSubject subject=new UOCSubject(new Subject(subjectID));
                
                // Get subjects for authenticated user
                ret=bussines.getSubjectActivities(subject);
                
                // Replace UOCSubjects by basic subjects
                for(Activity act:ret) {
                    Subject s=act.getSubject();
                    if( s instanceof UOCSubject) {
                        s=((UOCSubject)s).getSubject();
                        act.setSubject(s);
                    }
                }
              
            } catch (ExecPelpException ex) {
                Logger.getLogger(PelpServiceImpl.class.getName()).log(Level.SEVERE, null, ex);
            } catch (InvalidEngineException ex) {
                Logger.getLogger(PelpServiceImpl.class.getName()).log(Level.SEVERE, null, ex);
            } catch (AuthorizationException ex) {
                Logger.getLogger(PelpServiceImpl.class.getName()).log(Level.SEVERE, null, ex);
            } catch (InvalidSessionException ex) {
                Logger.getLogger(PelpServiceImpl.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
        
        return ret;
    }
    
   /* @Override
    public DeliverReport compileCode(String campusSession,String code,String progLanguage,Test[] tests) {
        DeliverReport result=null;
        
        if(bussines!=null) {
            try {
                // Set authentication information
                bussines.setCampusSession(campusSession);
                
                // User bussines method
                DeliverDetail deliverDetail=bussines.compileCode(code, progLanguage, tests);
                
                // Create output data
                result=getDeliverReport(deliverDetail);
            } catch (InvalidSessionException ex) {
                Logger.getLogger(PelpServiceImpl.class.getName()).log(Level.SEVERE, null, ex);
            } catch (ExecPelpException ex) {
                Logger.getLogger(PelpServiceImpl.class.getName()).log(Level.SEVERE, null, ex);
            } catch (InvalidEngineException ex) {
                Logger.getLogger(PelpServiceImpl.class.getName()).log(Level.SEVERE, null, ex);
            } catch (AuthorizationException ex) {
                Logger.getLogger(PelpServiceImpl.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
        
        return result;
    }
    
    @Override
    public DeliverDetail addDeliver(String campusSession,Activity activity, DeliverFile[] files) {
        DeliverDetail result=null;
        
        if(bussines!=null) {
            try {
                // Set authentication information
                bussines.setCampusSession(campusSession);
                
                // User bussines method
                result=bussines.addDeliver(activity, files);
                 
            } catch (InvalidSessionException ex) {
                Logger.getLogger(PelpServiceImpl.class.getName()).log(Level.SEVERE, null, ex);
            } catch (ExecPelpException ex) {
                Logger.getLogger(PelpServiceImpl.class.getName()).log(Level.SEVERE, null, ex);
            } catch (InvalidEngineException ex) {
                Logger.getLogger(PelpServiceImpl.class.getName()).log(Level.SEVERE, null, ex);
            } catch (AuthorizationException ex) {
                Logger.getLogger(PelpServiceImpl.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
        
        return result;
    }
    * 
    */
    
    @Override
    public DeliverDetail[] getDelivers(String campusSession,Activity activity) {
        DeliverDetail[] result=null;
        
        if(bussines!=null) {
            try {
                // Set authentication information
                bussines.setCampusSession(campusSession);
                
                // Set a UOCSubject type
                if(activity.getSubject()!=null) {
                    activity.setSubject(new UOCSubject(activity.getSubject()));
                }
                
                // User bussines method
                result=bussines.getUserDeliverDetails(activity);
                                
            } catch (InvalidSessionException ex) {
                Logger.getLogger(PelpServiceImpl.class.getName()).log(Level.SEVERE, null, ex);
            } catch (ExecPelpException ex) {
                Logger.getLogger(PelpServiceImpl.class.getName()).log(Level.SEVERE, null, ex);
            } catch (InvalidEngineException ex) {
                Logger.getLogger(PelpServiceImpl.class.getName()).log(Level.SEVERE, null, ex);
            } catch (AuthorizationException ex) {
                Logger.getLogger(PelpServiceImpl.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
        
        return result;
    }
    
    
    //MTOM Atachments
    /*public AttachmentResponse attachment(
			org.apache.ws.axis2.mtomsample.AttachmentRequest param0)
			throws Exception

	{
		AttachmentType attachmentRequest = param0.getAttachmentRequest();
		Base64Binary binaryData = attachmentRequest.getBinaryData();
		DataHandler dataHandler = binaryData.getBase64Binary();
		File file = new File(
				attachmentRequest.getFileName());
		FileOutputStream fileOutputStream = new FileOutputStream(file);
		dataHandler.writeTo(fileOutputStream);
		fileOutputStream.flush();
		fileOutputStream.close();
		
		AttachmentResponse response = new AttachmentResponse();
		response.setAttachmentResponse("File saved succesfully.");
		return response;
	}*/
}
