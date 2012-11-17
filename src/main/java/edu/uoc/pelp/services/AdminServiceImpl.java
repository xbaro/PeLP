/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package edu.uoc.pelp.services;

import edu.uoc.pelp.bussines.UOC.UOCPelpBussines;
import edu.uoc.pelp.model.vo.admin.PelpActiveSubjects;
import edu.uoc.pelp.model.vo.admin.PelpLanguages;

/**
 * Service for administrative tasks
 * @author Xavier
 */
//@WebService(serviceName = "AdminService")
public class AdminServiceImpl implements AdminService {
    
    private UOCPelpBussines bussines;
    
    /**
     * Default constructor
     */
    public AdminServiceImpl(UOCPelpBussines bussines) {
        super();
        this.bussines=bussines;
    }

    @Override
    public boolean addAdministrator(String userName) {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public boolean deleteAdministrator(String userName) {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public PelpActiveSubjects[] getActiveSubjects() {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public PelpActiveSubjects[] getActiveSubjects(String semester) {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public boolean addActiveSubject(String semester, String subject) {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public boolean removeActiveSubject(String semester, String subject) {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public boolean setActiveSubject() {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public boolean setActiveSemester(String semesterID, boolean status) {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public boolean addLanguage(String code, String description) {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public boolean removeLanguage(String code) {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public PelpLanguages[] getLanguages() {
        throw new UnsupportedOperationException("Not supported yet.");
    }

    @Override
    public boolean setLanguage(String code, String description) {
        throw new UnsupportedOperationException("Not supported yet.");
    }
    
    /**
     * This is a sample web service operation
     */
    /*@WebMethod(operationName = "hello")
    //public String hello(@WebParam(name = "name") String txt) {
    public String hello(String txt) {
        if(txt==null) {
            txt="<null>";
        }
        return "Hello " + txt + " !";
    }
    * */
    
    
}
