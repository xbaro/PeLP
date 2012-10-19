/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package edu.uoc.pelp.services;

/**
 * Service for administrative tasks
 * @author Xavier
 */
//@WebService(serviceName = "AdminService")
public class AdminServiceImpl {
    
    public AdminServiceImpl() {
        super();
    }
    
    /**
     * This is a sample web service operation
     */
    //@WebMethod(operationName = "hello")
    //public String hello(@WebParam(name = "name") String txt) {
    public String hello(String txt) {
        if(txt==null) {
            txt="<null>";
        }
        return "Hello " + txt + " !";
    }
}
