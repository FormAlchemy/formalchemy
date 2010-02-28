function(doc) { 
   if (doc.doc_type == "Person") 
    emit(doc._id, doc); 
}

