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
package edu.uoc.pelp.engine.aem;

import edu.uoc.pelp.engine.aem.exception.CompilerAEMPelpException;
import edu.uoc.pelp.engine.aem.exception.PathAEMPelpException;
import java.io.*;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Locale;
import java.util.Scanner;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.tools.*;

/**
 * This class implements the Code Analyzer for the Java programming language.
 * @author Xavier Baró
 */
public class JavaCodeAnalyzer extends BasicCodeAnalyzer {
    
    /**
     * List of generated files.
     */
    private ArrayList<File> _outputFiles=new ArrayList<File>();
    
     /**
     * List of input files.
     */
    private ArrayList<File> _inputFiles=new ArrayList<File>();
        
    public BuildResult build(CodeProject project) throws PathAEMPelpException, CompilerAEMPelpException {
        BuildResult result=new BuildResult();

        // Create the list of input files and expected output files
        for(File f:project.getRelativeFiles()) {
            if(isAccepted(f)) {
                // Add the absolute path to the input files
                _inputFiles.add(project.getAbsolutePath(f, null));                

                // Add output path                
                if(getFileExtension(f).equalsIgnoreCase(".java")) {
                    _outputFiles.add(project.getAbsolutePath(changeExtension(f,".class"), _workingPath));
                }
            }
        }

        // Check that working path exists and is valid
        if(_workingPath!=null) {
            // If not exist create it
            if(!_workingPath.exists()) {
                if(!_workingPath.mkdirs()) {
                    throw new PathAEMPelpException("Cannot create the working path <" + _workingPath.getAbsolutePath() + ">");
                }
            }

            // Check that it is a directory 
            if(!_workingPath.isDirectory()) {
                throw new PathAEMPelpException("Working path <" + _workingPath.getAbsolutePath() + "> is not a directory");
            }

            // Check that is writable
            if(!_workingPath.canWrite()) {
                throw new PathAEMPelpException("Working path <" + _workingPath.getAbsolutePath() + "> is not writable");
            }
        }

        // Prepare the input files
        File[] inFiles=new File[_inputFiles.size()];
        _inputFiles.toArray(inFiles);

        // Prepare the compiler
        DiagnosticCollector<JavaFileObject> diagnostics = new DiagnosticCollector<JavaFileObject>();
        JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
        StandardJavaFileManager fileManager = compiler.getStandardFileManager(diagnostics, null, null);
        Iterable<? extends JavaFileObject> compilationUnits =
            fileManager.getJavaFileObjectsFromFiles(Arrays.asList(inFiles));       
        
        // Perform compilation
        result.start();
        boolean compRes=compiler.getTask(null, fileManager, diagnostics, null, null, compilationUnits).call();
        
        // Collect the errors
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        PrintStream compilerMessage = new PrintStream(baos);
        for (Diagnostic diagnostic : diagnostics.getDiagnostics()) {
            compilerMessage.format("Error on line %d in %s:\n", 
                    diagnostic.getLineNumber(),
                    diagnostic.getSource());
            compilerMessage.format("%s\n",diagnostic.getMessage(Locale.ENGLISH));
        }
        
        // Set the final results
        result.setResult(compRes, baos.toString());
        
        try {
            // Close the file manager
            fileManager.close();
        } catch (IOException ex) {
            Logger.getLogger(JavaCodeAnalyzer.class.getName()).log(Level.SEVERE, null, ex);
            result.setResult(false, "Unexpected error.");
        }
        
        // Check that output files are generated 
        if(result.isCorrect()) {
            for(File outFile:_outputFiles) {
                if(!outFile.exists()) {
                    result.setResult(false, "Output file <" + outFile + "> does not exist.");
                    break;                    
                }
            }
        }
        
        return result;
    }

    public String getLanguageID() {
        return "JAVA";
    }

    @Override
    protected String[] getAllowedExtensions() {
        String[] exts={".java"};
        return exts;
    }

    @Override
    protected boolean isMainFile(File file) {
        //TODO: Remove comments before search for main function and use more sofisticated patterns
        boolean isMain=false;
        Scanner scanner=null;
        try {
            scanner = new Scanner(new FileInputStream(file), "UTF-8");
            while (scanner.hasNextLine() && !isMain){
                String line=scanner.nextLine();
                if(line.trim().indexOf("public static void main(String".trim())>=0) {
                    isMain=true;
                }
            }
        } catch (FileNotFoundException ex) {
            isMain=false;
        } finally{
            if(scanner!=null) {
                scanner.close();
            }
        }
        
        return isMain;
    }
}
